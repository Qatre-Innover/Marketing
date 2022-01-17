from flask import Flask
from flask.templating import render_template
from flask.helpers import url_for
from flask import request
from werkzeug.utils import redirect
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
import pickle as pkl
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
warnings.filterwarnings(action="ignore")

# Loading the flask app, sample of the dataset and our pre-trained clustering model.
app = Flask(__name__)
data = pd.read_csv(".\cust_seg.csv")
model = pkl.load(open("./Pipeline_customer.pickle", "rb"))

data.drop(columns=["Unnamed: 0"], inplace=True)

# Missing values imputation.
imputer = SimpleImputer(strategy = 'mean')
data["Income"] = imputer.fit_transform(data[["Income"]])

# Feature Engineering. (Refer to jupyter notebook for details.)
data["kids"] = data["Kidhome"] + data["Teenhome"]
data["Age"] = 2021 - data["Birth_Year"]
data["date_parsed"] = pd.to_datetime(data["date_parsed"])
data["loyal_for_#_month"] = 12.0 * (2021 - data.date_parsed.dt.year ) + (1 - data.date_parsed.dt.month)
data["total_spending"] = data["MntWines"] + data["MntFruits"] + data["MntMeatProducts"] + data["MntFishProducts"] + data["MntSweetProducts"] + data["MntGoldProds"]
data.loc[(data['Age'] >= 13) & (data['Age'] <= 19), 'AgeGroup'] = 'Teen'
data.loc[(data['Age'] >= 20) & (data['Age']<= 39), 'AgeGroup'] = 'Adult'
data.loc[(data['Age'] >= 40) & (data['Age'] <= 59), 'AgeGroup'] = 'Middle Age Adult'
data.loc[(data['Age'] > 60), 'AgeGroup'] = 'Senior Adult'
marriage_dict = {
    'Together': 'Partner',
    'Married' : 'Partner',
    'Divorced' : 'Single',
    'Widow' : 'Single',
    'Alone' : 'Single',
    'Absurd' : 'Single',
    'YOLO' : 'Single'
}
data["Marital_Status"] = data["Marital_Status"].replace(marriage_dict)
data["family_size"] = data["kids"] + data["Marital_Status"].replace({'Single': 1, 'Partner': 2})
data["Is_parent"] = np.where(data["kids"] > 0, 1, 0)
data["Education"] = data["Education"].replace({
    "Basic":"Undergraduate",
    "2n Cycle":"Undergraduate", 
    "Graduation":"Graduate", 
    "Master":"Postgraduate", 
    "PhD":"Postgraduate"
})

data_new = data.copy()
data_new.drop(['date_parsed', 'Z_CostContact', 'Z_Revenue', 'Birth_Year', 'ID', 'AgeGroup', \
               'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5', 'AcceptedCmp1','AcceptedCmp2', 'Complain', 'Response'], 
             axis = 1, inplace = True)

categorical_columns = data_new.select_dtypes(include = ["object"]).columns

encoder = LabelEncoder()
for i in categorical_columns:
    data_new[i] = data_new[[i]].apply(encoder.fit_transform)

# Sample dataset customer clustering using production pipeline.
pipe_preds = model.predict(data_new)
print(pipe_preds)

customer = pd.DataFrame({"ID": np.array(data.ID), "Cluster": np.array(pipe_preds)})
tiers = {
    0: 'Platinum',
    2: 'Gold',
    3: 'Silver',
    1: 'Bronze'
}

customer["membership_tier"] = customer["Cluster"].replace(tiers)
print(customer)


# Flask app routes.
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/customer-rfm-analysis")
def customerseg():
    return render_template("customer.html")

@app.route("/contactus")
def contact():
    return render_template("contactUs.html")

@app.route("/customer-rfm-analysis/user", methods = ['POST'])
def user():
    if request.method  == 'POST':
        id = request.form["Id"]
        id = int(id)
        if id in np.array(data.ID):
            ans = 1
            print("Customer ID is: ", id)
            tier = list(customer.membership_tier[( customer["ID"] == id )])[0]
            print(tier)
            if tier == 'Platinum':
                counter = 0
            elif tier == 'Gold':
                counter = 2
            elif tier == 'Silver':
                counter = 3
            else:
                counter = 1
            opc = '40%'

            return render_template("customer.html", tier = tier, counter = counter, opc = opc, ans = ans)
        
        else:
            ans = -1
            return render_template("customer.html", response = ans)
    

# Driver Code.
if __name__ == "__main__":
    app.run(debug = True, port = 8080)

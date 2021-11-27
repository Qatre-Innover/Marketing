import re
from flask import Flask
from flask.templating import render_template
from flask.helpers import url_for
from flask import request
from werkzeug.utils import redirect
import pandas

app = Flask(__name__)

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
        ID = request.form["Id"]
    print("Customer ID is: ", ID)

    
    return render_template("customer.html")


if __name__ == "__main__":
    app.run(debug = True, port = 8080)

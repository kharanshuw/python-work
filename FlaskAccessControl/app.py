# Import required modules
import os

from flask import (
    Flask,
    jsonify,
    request,
)  # Flask: web framework, jsonify: return JSON, request: access HTTP request data
import mysql.connector  # For MySQL database connection
from flask_bcrypt import Bcrypt
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

bcrypt = Bcrypt(app)

secret_key = os.getenv("secret_key")

app.secret_key = secret_key


def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        mysql.connector.connect(
            host=os.getenv("host"), user=os.getenv("user"), password=os.getenv("password"),
            database=os.getenv("database")
        )


if __name__ == "__main__":
    print("connecting to db....")
    app.run(debug=True)

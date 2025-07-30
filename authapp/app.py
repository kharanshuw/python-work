from ast import And
from codecs import utf_8_decode
from enum import unique
import os
from click import password_option
from flask import Flask,render_template,request,session,redirect, url_for
import bcrypt
import secrets
import mysql.connector
import mysql.connector.cursor
import logging
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

app = Flask(__name__)

load_dotenv()

bcrypt = Bcrypt(app)

# Configure logging to write debug messages to a file
logging.basicConfig(filename="record.log",level=logging.DEBUG)

# Generate a random secret key for session management
secrets_key = os.getenv("secret_key")
app.secret_key = secrets_key


# Route for user registration.
# GET: Renders the registration form.
#     POST: Registers a new user by inserting their email and password into MySQL.
@app.route("/",methods=["GET","POST"])
def register():
    if request.method == "GET":
        app.logger.info("running get request of register")
    
        return render_template("register.html")
    else:

        app.logger.info("running post request of register")


        username = request.form["email"]
        password = request.form["password"]

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        

        con = mysql.connector.connect(
            host= os.getenv("host"),
            user = os.getenv("db_user"),
            password = os.getenv("db_password"),
            database = os.getenv("database")
        )

        cursor = con.cursor()
        

         # SQL query to insert the user into the database
        sql_query = "INSERT INTO testflask (email,password ) VALUES(%s,%s);"

        app.logger.info("executing insert query")

        cursor.execute(sql_query,(username,hashed_password))

        app.logger.info("executing successfull of data insertion")

        con.commit()

        cursor.close()

        con.close()

        return redirect(url_for("register_success"))
    

# Route for user login.

#     GET: Renders the login form.
#     POST: Verifies user's credentials and starts a session on success.
@app.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":



        app.logger.info("running get request of login ")


        username = request.form["email"]

        password = request.form["password"]

        



        app.logger.info("username and password are "+username+" : "+password)


        con = mysql.connector.connect(
            host= os.getenv("host"),
            user = os.getenv("db_user"),
            password = os.getenv("db_password"),
            database = os.getenv("database")
        )


        cursor = con.cursor(dictionary=True)
        
         # SQL query to fetch the user with the provided email
        sql_query = "SELECT * from testflask WHERE email = %s"

        app.logger.info("Executing the fetch query in DB...")


        cursor.execute(sql_query,(username,))

        user = cursor.fetchone()

        app.logger.info("Fetched user details:")

        
        app.logger.info("user email "+user["email"])
        
        
        db_password = user["password"]

        db_username = user["email"]

        is_valid = bcrypt.check_password_hash(db_password,password)

        
        app.logger.info(f"is valid result {is_valid}")

        if is_valid and username == db_username:
            app.logger.info("same password and username")
            session["user_id"] = username

            return redirect(url_for("login_success"))
        else:
            app.logger.info("diff password")



        return "ok"




    else:
        app.logger.info("running get request of login ")
        return render_template("login.html")


@app.route("/login_successfully")
def login_success():
    return "login successfully!"


@app.route("/register-success")
def register_success():
    return "Registered successfully!"



if __name__ == "__main__":
    print("connecting to db....")
    app.run(debug=True)
        

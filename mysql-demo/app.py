# Import required modules
import mysql.connector  # For MySQL database connection
from flask import (
    Flask,
    jsonify,
)  # Flask: web framework, jsonify: return JSON, request: access HTTP request data

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)


# Define the default route for the home page
@app.route("/")
def hello_world():
    return "Hello World"


# Define route to fetch student data by ID using a GET request
@app.route("/fetchbyid/<int:id>", methods=["GET"])
def fetchbyid(id):
    app.logger.info(f"id recieved is {id}")

    sql_query = "select * from student where id=%s"

    con = mysql.connector.connect(
        host="localhost", user="root", password="root", database="test"
    )

    cursor = con.cursor(dictionary=True)

    cursor.execute(sql_query,(id,))

    data = cursor.fetchall()

    cursor.close()

    con.close()

    return jsonify(data)


if __name__ == "__main__":
    print("connecting to db....")
    app.run(debug=True, port=8080)

# Import required modules
from flask import (
    Flask,
    jsonify,
    request,
)  # Flask: web framework, jsonify: return JSON, request: access HTTP request data
import mysql.connector  # For MySQL database connection

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)


# Define the default route for the home page
@app.route("/")
def hello_world():
    return "Hello World"


# Define a GET route to fetch all table names from the 'test' database
@app.route("/insertdata", methods=["POST"])
def gettables():

    # Route to insert data into the 'student' table in the MySQL database.

    # Expects:
    #     JSON payload with 'name' and 'marks' fields.

    # Returns:
    #     JSON response with a success message and HTTP 200 status code.

    # Establish a connection to the MySQL database
    con = mysql.connector.connect(
        host="localhost", user="root", password="root", database="test"
    )

    # Create a cursor object to execute SQL queries
    cursor = con.cursor()

    # Get JSON data from the request body
    data = request.get_json()

    # Extract 'name' and 'marks' from the JSON payload
    name = data.get("name")

    marks = data.get("marks")

    # Prepare SQL query for inserting data into the student table
    sql_query = "INSERT INTO student(name,marks) values (%s,%s)"

    # Execute the SQL query with actual values
    cursor.execute(sql_query, (name, marks))

    # Commit the transaction to save changes in the database
    con.commit()

    # close the connection and cursor
    cursor.close()
    con.close()

    return jsonify({"message": "posted"}), 200


if __name__ == "__main__":
    print("connecting to db....")
    app.run(debug=True, port=8080)

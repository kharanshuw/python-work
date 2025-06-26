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
@app.route("/gettables", methods=["GET"])
def gettables():
    # Establish a connection to the MySQL database
    con = mysql.connector.connect(
        host="localhost", user="root", password="root", database="test"
    )
    # Create a cursor object to interact with the database
    cursor = con.cursor()

    # Execute SQL command to list all tables in the database

    cursor.execute("show tables;")

    # Fetch all table names (each as a tuple like: ('table_name',))
    tables = cursor.fetchall()

    # Close the cursor and connection (important to free up resources)

    cursor.close()
    con.close()

    # Initialize an empty list to store clean table names
    table_names = []

    # Iterate through fetched tables and extract only the table name (string)

    for i in tables:
        print(f"printing table name {i}")
        table_names.append(i[0])  # i[0] extracts the name from the tuple

    # Return the list of table names in JSON format with HTTP status code 200 (OK)
    return jsonify({"tables": table_names}), 200


if __name__ == "__main__":
    print("connecting to db....")
    app.run(debug=True)

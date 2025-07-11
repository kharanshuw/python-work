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


# Define a route '/fetchAll' that handles GET requests
@app.route("/fetchAll")
def fetch_all():
    # Connect to the MySQL database using credentials and target DB
    con = mysql.connector.connect(
        host="localhost", user="root", password="root", database="test"
    )

    # Create a cursor with dictionary=True to return rows as dictionaries
    cursor = con.cursor(dictionary=True)

    # Define the SQL query to fetch all records from the 'student' table
    sql_query = "select * from student"

    # Fetch all rows returned by the query as a list of dictionaries
    cursor.execute(sql_query)

    rows = cursor.fetchall()

    cursor.close()

    con.close()

    return jsonify(rows)


if __name__ == "__main__":
    print("connecting to db....")
    app.run(debug=True, port=8080)

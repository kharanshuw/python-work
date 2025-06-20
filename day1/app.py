# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask,redirect,url_for,request,render_template
from flask_mysqldb import MySQL



# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'test'


# initialize mysql app 
mysql = MySQL(app)


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("select * from users")

    users = cur.fetchall()

    cur.close()

    return render_template('home.html',users =users)

@app.route('/add_user', methods=['POST'])
def add_users():
    name = request.form['name']
    cur = mysql.connection.cursor()
    cur.execute("Insert into users (name ) values (%s)",(name,))
    mysql.connection.commit()
    cur.close()
    return redirect('/')


# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=True)
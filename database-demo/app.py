from email.policy import default

from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
  sno = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80),nullable= False)
  password = db.Column(db.String(80),nullable=False)
  datetime = db.Column(db.DateTime,default=datetime.utcnow())
  


@app.route("/")
def hello():
  return "Hello World!"
 

@app.route("/register")
def register():
  return render_template("base.html")



if __name__ == "__main__":
  app.run(debug=True)
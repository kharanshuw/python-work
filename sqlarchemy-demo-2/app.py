from email.policy import default

from flask import Flask,render_template,request,session,redirect
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
  

with app.app_context():
  db.create_all()


@app.route("/")
def hello():
  all_user = User.query.all()
  return render_template("home.html",alluser = all_user)
 

@app.route("/register",methods=['POST',"GET"])
def register():
  if request.method == "POST":
    username = request.form["username"]
    password = request.form["password"]

    new_user = User(
      username = username,
      password = password
    )

    db.session.add(new_user)
    db.session.commit()

    return redirect("/register")


  else:
    return render_template("base.html")
  


  



if __name__ == "__main__":
  app.run(debug=True)
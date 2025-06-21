
from flask import Flask,render_template,request
app = Flask(__name__)

@app.route("/")
def hello():
  return "Hello World!"


@app.route("/login")
def login():
  return render_template("base.html")



@app.route("/processlogin",methods=["POST"])
def processlogin():
  if request.method == "POST":
    username = request.form["email"]
    password = request.form['password']
    print(f"printing username and password {username} and {password}")
  return render_template("base.html")

if __name__ == "__main__":
  app.run(debug=True)
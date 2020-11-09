import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/set_goals")
def set_goals():

    goals = mongo.db.goals.find()
    return render_template("goals.html", goals=goals)


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        if request.method == "POST":
            # check if email already exists in db
            existing_user = mongo.db.users.find_one(
                {"email": request.form.get("email").lower()})

            if existing_user:
                flash("Email already exists")
                return redirect(url_for("register"))

            register = {
                "username": request.form.get("username").lower(),
                "email": request.form.get("email").lower(),
                "password": generate_password_hash(
                                request.form.get("password"))
            }
            mongo.db.users.insert_one(register)

            # put the new user into "session" cookie
            session["user"] = request.form.get("username").lower()
            flash("You are now registered!")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form_get("username").lower()})

        if existing_user:
            # ensure hashed password matches input from user
            if check_password_hash(
                   existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome {}".format(request.form.get("username")))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/new_goal", methods=["GET", "POST"])
def new_goal():
    if request.method == "POST":
        select = request.form.get("category_name")
        new_goal = {
                "category_name": request.form.get(str(select)),
                "goal_title": request.form.get("goal_title"),
                "goal_description": request.form.get("goal_description"),
                "due_date": request.form.get("due_date"),
            }
        mongo.db.goals.insert_one(new_goal)

    return render_template("new-goal.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

from flask import render_template, url_for, flash, redirect
from app import app
from app.forms import LoginForm

'''Stores all the routes/views within the web app'''

@app.route("/")
@app.route("/home")
def home():
    user = {"username": "Adrian"}
    posts = [{
        "title": "Squash Mens win 3-1",
         "body": "Lorem, ipsum dolor sit amet consectetur adipisicing elit. Molestias aut, repellat ipsum facere voluptate dicta obcaecati deserunt nobis suscipit eaque?",
         "date": "12/04/21"
         },
         {
        "title": "Rugby Womens win 30-12",
         "body": "Lorem, ipsum dolor sit amet consectetur adipisicing elit. Molestias aut, repellat ipsum facere voluptate dicta obcaecati deserunt nobis suscipit eaque?",
         "date": "14/05/22"
         }]
    return render_template("home.html", title="Home Page", user=user, posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f"Your username is {form.username.data}, password {form.password.data}, remember me = {form.remember_me.data}")
        return redirect(url_for("login"))
    return render_template("login.html", title="Login", form=form)

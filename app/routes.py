from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
# Login
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, UserRoles, Role, Post
# Next page
from werkzeug.urls import url_parse

'''Stores all the routes/views within the web app'''

@app.route("/")
@app.route("/home")
@login_required
def home():
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
    return render_template("home.html", title="Home Page", posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        # check for user
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash("Username or password is incorrect.")
            return redirect(url_for("login"))
        # check if password matches
        login_user(user, remember=form.remember_me.data)
        # implement next page feature
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)
    return render_template("login.html", title="Login", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Hi {} You have successfully registered!".format(user.username))
        return(redirect(url_for("home")))
    return render_template("registration.html", title="Register", form=form)


@app.route("/user/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    # Prepopulate form with user's current data
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        # Automatically update the user object with the submitted form data
        form.populate_obj(user)
        db.session.commit()
        flash("Changes have been made successfully.")
        return redirect(url_for("profile", username=user.username))
    return render_template("profile.html", title="Profile", form=form, user=user)



@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("home"))
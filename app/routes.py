from flask import render_template, url_for, flash, redirect, request, session
from sqlalchemy import desc, asc
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EditSportPageForm, SearchUserForm, EditUserRolesForm, AddSportForm
# Login
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, UserRoles, Role, Post, Sport
# Next page
from werkzeug.urls import url_parse
# Roles
import flask_authorization

@app.route("/")
@app.route("/home")
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

# ------------------------------------------ #
# ------------- Authentication ------------- #
# ------------------------------------------ #
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
    return render_template("auth/login.html", title="Login", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("home"))


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
        login_user(user)
        flash("Hi {}.You have successfully registered! Please update your details below.".format(user.username))
        return(redirect(url_for("profile", username=user.username)))
    return render_template("auth/registration.html", title="Register", form=form)

# ------------------------------------------ #
# ------------------ User ------------------ #
# ------------------------------------------ #
@app.route("/user/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    # Prepopulate form with user's current data
    user_data = {
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Email": user.email,
        "About Me": user.about_me,
        "Company": user.company,
        "Platoon": user.platoon,
        "Section": user.section,
    }
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        # Automatically update the user object with the submitted form data
        form.populate_obj(user)
        db.session.commit()
        flash("Changes have been made successfully.")
        return redirect(url_for("profile", username=user.username))
    return render_template("profile.html", title="Profile", form=form, user=user, user_data=user_data)

# ------------------------------------------ #
# ------------------ Admin ----------------- #
# ------------------------------------------ #
@app.route("/admin", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required("admin")
def admin():
    return render_template("admin/admin.html", title="Admin Page")


@app.route("/admin/edit_roles", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required("admin")
def edit_roles(user=None):
    search_form = SearchUserForm()
    roles_form = EditUserRolesForm()

    if search_form.submit1.data and search_form.validate_on_submit():
        user = User.query.filter_by(username=search_form.username.data).first()

        if user:
            return redirect(url_for('admin_search', username=user.username))

        flash('User not found. Please try again.')
        return redirect(url_for('edit_roles'))
    elif roles_form.validate_on_submit():
        flash('Please search for a user.')
    return render_template("admin/edit_roles.html", title="Edit User Roles", search_form=search_form, roles_form=roles_form)


@app.route("/admin/edit_roles/<username>", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required("admin")
def admin_search(username):
    user = User.query.filter_by(username=username).first_or_404()
    search_form = SearchUserForm()
    roles_form = EditUserRolesForm()
    add_sport_form = AddSportForm()
    if search_form.submit1.data and search_form.validate_on_submit():
        user = User.query.filter_by(username=search_form.username.data).first()

        if user:
            return redirect(url_for('admin_search', username=user.username))

        flash('User not found. Please try again.')
        return redirect(url_for('edit_roles'))
    else:
        search_form.username.data = user.username

    if roles_form.submit2.data and roles_form.validate_on_submit():
        roles = {
            "staff": roles_form.staff.data,
            "sport_oic": roles_form.sport_oic.data,
            "admin": roles_form.admin.data}
        user.add_roles(username=user.username, roles=roles)
    
    if user:
        for role in user.roles:
            roles_form[role.name].data = True

    return render_template("admin/edit_roles.html", title="Admin Page", search_form=search_form, roles_form=roles_form, add_sport_form=add_sport_form, user=user)

@app.route("/admin/edit_sports", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required("admin")
def edit_sports(user=None):
    sport_form = AddSportForm()
    if sport_form.validate_on_submit():
        sport = Sport(name=sport_form.name.data.lower(),
                      description=sport_form.description.data,
                      sport_oic=sport_form.sport_oic.data,
                      sport_oic_email=sport_form.sport_oic_email.data,
                      img_src=sport_form.img_src.data,
                      capacity=sport_form.capacity.data,
                      location=sport_form.location.data,
                      timing=sport_form.timing.data,
                      )
        db.session.add(sport)
        db.session.commit()
        flash("{} has been successfully created!".format(sport_form.name.data))
    return render_template("admin/edit_sports.html", title="Edit User Roles", sport_form=sport_form)

# ------------------------------------------ #
# ----------------- Sports ----------------- #
# ------------------------------------------ #
@app.route('/sports/<name>', methods=["GET", "POST"])
def sport_page(name):
    sport = Sport.query.filter_by(name=name).first_or_404()
    form = EditSportPageForm(obj=sport)
    if form.validate_on_submit():
        form.populate_obj(sport)
        db.session.commit()
        flash("Changes have been made successfully.")
        return redirect(url_for("sport_page", name=name))
    return render_template("sport_page.html", sport=sport, form=form)


@app.route("/sports")
def sports():
    sports = Sport.query.order_by(Sport.name.asc()).all()
    return render_template("sports.html", sports=sports)



from flask import render_template, url_for, flash, redirect, request, session
from sqlalchemy import desc, asc
from app import app, db
from app.models import User, UserRoles, Role, Post, Sport, File
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EditSportPageForm, SearchUserForm, EditUserRolesForm, AddSportForm, TrackStudentForm, StudentAttendanceForm, TrackSportForm
# Login
from flask_login import current_user, login_user, logout_user, login_required
# Next page
from werkzeug.urls import url_parse
# Upload files
from upload_files import upload_profile_photo, delete_profile_photo, allowed_file, PROFILE_PHOTO_BUCKET_NAME
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
        user = User(username=form.username.data,
                    email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    company=form.company.data,
                    platoon=form.platoon.data,
                    section=form.section.data)
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
    # Restrict viewing other profiles to staff
    if not current_user.get_permissions() and username != current_user.username:
        flash("You are not permitted to view other profiles.")
        return redirect(url_for('home'))
    
    user = User.query.filter_by(username=username).first_or_404()
    if user.profile_photo_id:
        file = File.query.filter_by(id=user.profile_photo_id).first()
        profile_photo = f"https://{PROFILE_PHOTO_BUCKET_NAME}.s3.amazonaws.com/{file.filename}"
    else:
        profile_photo = None
    # Prepopulate form with user's current data
    user_data = {
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Email": user.email,
        "Company": user.company,
        "Platoon": user.platoon,
        "Section": user.section,
    }
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        # Automatically update the user object with the submitted form data
        form.populate_obj(user)
        profile_photo = request.files["profile_photo"]
        # Check if photo is valid
        if profile_photo and not allowed_file(profile_photo.filename):
            flash("Please upload using the correct file type (jpg, jpeg, png)")
            return redirect(url_for("profile", username=user.username))
        # Delete user profile photo if it exists
        if profile_photo and user.profile_photo_id is not None:
            try:
                file = File.query.filter_by(id=user.profile_photo_id).first()
                # Delete photo from S3 bucket
                delete_profile_photo(file.id)
                # Delete photo from database
                db.session.delete(file)
                db.session.commit()
            except AttributeError:
                pass
        if profile_photo:
            upload_profile_photo(user=user, profile_photo=profile_photo)
            db.session.commit()
            return redirect(url_for('profile', username=current_user.username))
        flash("Changes have been made successfully.")
        db.session.commit()
        return redirect(url_for("profile", username=user.username))
    return render_template("profile.html", title="Profile", form=form, user=user, user_data=user_data, profile_photo=profile_photo)

# ------------------------------------------ #
# ------------------ Admin ----------------- #
# ------------------------------------------ #
@app.route("/admin", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required(["admin"])
def admin():
    return render_template("admin/admin.html", title="Admin Page")


# Edit user roles - Admin, Sports OIC, Staff
@app.route("/admin/edit_roles", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required(["admin"])
def edit_roles():
    search_form = SearchUserForm()
    roles_form = EditUserRolesForm()

    users_with_roles = User.query.filter(User.roles != None).all()
    if search_form.submit1.data and search_form.validate_on_submit():
        user = User.query.filter_by(username=search_form.username.data).first()
        if user:
            return redirect(url_for('admin_search', username=user.username))
        flash('User not found. Please try again.')
        return redirect(url_for('edit_roles'))
    elif roles_form.validate_on_submit():
        flash('Please search for a user.')
    return render_template("admin/edit_roles.html", title="Edit User Roles", search_form=search_form, roles_form=roles_form, users_with_roles=users_with_roles, user=None)


@app.route("/admin/edit_roles/<username>", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required(["admin"])
def admin_search(username):
    # Find user in database
    user = User.query.filter_by(username=username).first_or_404()
    # Initialise forms
    search_form = SearchUserForm()
    roles_form = EditUserRolesForm()
    add_sport_form = AddSportForm()
    # Get list of users with roles attached
    users_with_roles = User.query.filter(User.roles != None).all()
    if search_form.submit1.data and search_form.validate_on_submit():
        user = User.query.filter_by(username=search_form.username.data).first()
        if user:
            return redirect(url_for('admin_search', username=user.username))
        flash('User not found. Please try again.')
        return redirect(url_for('edit_roles'))
    else:
        search_form.username.data = user.username
    # Update roles of user based off form
    if roles_form.submit2.data and roles_form.validate_on_submit():
        roles = {
            "staff": roles_form.staff.data,
            "sport_oic": roles_form.sport_oic.data,
            "admin": roles_form.admin.data}
        user.add_roles(username=user.username, roles=roles)
    # Prepopulate roles_form with user roles
    if user:
        for role in user.roles:
            roles_form[role.name].data = True
    return render_template("admin/edit_roles.html", title="Admin Page", search_form=search_form, roles_form=roles_form, add_sport_form=add_sport_form, user=user, users_with_roles=users_with_roles)


@app.route("/admin/edit_sports", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required(["admin"])
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


@app.route("/track/section", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required(["admin", "sports_oic", "staff"])
def track_section():
    form = TrackStudentForm()
    return render_template("admin/track_section.html", form=form)


@app.route("/track/section/search", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required(["admin", "sports_oic", "staff"])
def track_section_search():
    form = TrackStudentForm()
    if form.validate_on_submit():
        users = User.query.filter_by(platoon=form.platoon.data, section=form.section.data).all()
    else:
        flash("Please try again.")
        return redirect(url_for('track_section'))
    return render_template("admin/track_section.html", form=form, users=users, sports=sports)


@app.route("/track/sport", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required(["admin", "sports_oic", "staff"])
def track_sport():
    form = TrackSportForm()
    attendance_form = StudentAttendanceForm()
    if attendance_form.validate_on_submit():
        flash("Please search for a sport first.")
        return redirect(url_for('track_sport'))
    return render_template("admin/track_sport.html", form=form, attendance_form=attendance_form)


@app.route("/track/sport/search", methods=["GET", "POST"])
@login_required
@flask_authorization.permission_required(["admin", "sports_oic", "staff"])
def track_sport_search():
    form = TrackSportForm()
    attendance_form = StudentAttendanceForm()
    if form.submit.data and form.validate_on_submit():
        sport = Sport.query.filter_by(name=form.sport.data.lower()).first()
        users = User.query.filter_by(sport_id=sport.id).all()
        session["sport"] = sport.id
    if attendance_form.submit_attended.data and attendance_form.validate_on_submit():
        users = User.query.filter_by(sport_id=session["sport"]).all()
        flash("Nominal roll submitted.")
        students_attended = request.form.getlist('attended')
        for user in users:
            user.nominal_submitted = True
            if str(user.id) in students_attended:
                user.attended_sport = True
            else:
                user.attended_sport = False
        db.session.commit()
        return redirect(url_for('track_sport'))
    return render_template("admin/track_sport.html", form=form, attendance_form=attendance_form, users=users)



# ------------------------------------------ #
# ----------------- Sports ----------------- #
# ------------------------------------------ #
@app.route("/sports")
def sports():
    sports = Sport.query.order_by(Sport.name.asc()).all()
    return render_template("sports.html", sports=sports)


@app.route('/sports/<name>', methods=["GET", "POST"])
def sport_page(name):
    sport = Sport.query.filter_by(name=name).first_or_404()
    form = EditSportPageForm(obj=sport)
    users = User.query.filter_by(sport_id=sport.id).all()
    if form.submit.data and form.validate_on_submit():
        form.populate_obj(sport)
        db.session.commit()
        flash("Changes have been made successfully.")
        return redirect(url_for("sport_page", name=name))
    return render_template("sport_page.html", sport=sport, form=form, users=users)


@app.route('/sports/<name>/signup', methods=["GET", "POST"])
def sign_up_to_sport(name):
    sport = Sport.query.filter_by(name=name).first_or_404()
    if current_user.sport_id == sport.id:
        flash("You are no longer signed up to {}".format(sport.name.capitalize()))
        current_user.unsign_up_to_sport(sport.name)
        current_user.attended_sport = False
        current_user.nominal_submitted = False
        db.session.commit()
    else:
        flash("You are now signed up to {}".format(sport.name.capitalize()))
        current_user.sign_up_to_sport(sport.name)
        current_user.attended_sport = False
        current_user.nominal_submitted = False
        db.session.commit()
    return redirect(url_for("sport_page", name=name))
'''Stores all the form logic for web app'''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField, EmailField, FileField, MultipleFileField, IntegerField, SelectField, URLField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Submit")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Please use a different username.")
        
    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("That email is already registed.")

class EditProfileForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    about_me = TextAreaField("About Me", validators=[DataRequired(), Length(max=140)])
    company = SelectField("Company", choices=["Normandy", "Helmand", "Basra", "Alamein"], validators=[DataRequired()])
    platoon = StringField("Platoon", validators=[DataRequired()])
    section = SelectField("Section", choices=["1", "2", "3", "4"], validators=[DataRequired()])
    submit = SubmitField("Make Changes")
    
class EditSportPageForm(FlaskForm):
    description = TextAreaField("Sport Description", validators=[DataRequired()])
    sport_oic = StringField("Sport OIC", validators=[DataRequired()])
    sport_oic_email = EmailField("Sport OIC email", validators=[DataRequired(), Email()])
    location = StringField("Location", validators=[DataRequired()])
    timing = StringField("Timing", validators=[DataRequired()])
    capacity = IntegerField("Capacity", validators=[DataRequired()])
    img_src = StringField("Header Image Source", validators=[DataRequired()])
    submit = SubmitField("Make Changes")

class SearchUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    submit1 = SubmitField("Search")

class EditUserRolesForm(FlaskForm):
    staff = BooleanField("Staff")
    sport_oic = BooleanField("Sport OIC")
    admin = BooleanField("Admin")
    submit2 = SubmitField("Edit User Roles")

class AddSportForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    sport_oic = StringField("Sport OIC", validators=[DataRequired()])
    sport_oic_email = EmailField("Sport OIC email", validators=[DataRequired(), Email()])
    location = StringField("Location")
    timing = StringField("Timing")
    capacity = IntegerField("Capacity")
    img_src = URLField("Image Source", validators=[DataRequired()])
    submit = SubmitField("Create sport")
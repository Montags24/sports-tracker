from flask import Flask
from config import Config
# Database config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# Login
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)
# Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Login
login = LoginManager(app)
# Send user to login page if page requires login
login.login_view = "login"

from app import routes, models
from flask import Flask
from config import Config
# Database config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# Login
from flask_login import LoginManager
# Logging
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os


app = Flask(__name__)
app.config.from_object(Config)
# Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Login
login = LoginManager(app)
# Send user to login page if page requires login
login.login_view = "login"

from app import routes, models, errors

# Send error reports if app is in production mode
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        # Logging to a file
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/sports-tracker.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Sports-Tracker startup')
import boto3
import uuid

from app import app, db
from app.models import User, Sport, File
from flask import Flask, redirect, url_for, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy 

s3 = boto3.resource('s3')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
PROFILE_PHOTO_BUCKET_NAME = "sports-profile-photos"
SPORTS_PHOTO_BUCKET_NAME = "sports-gallery"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_new_filename(filename):
    return uuid.uuid4().hex + "." + filename.rsplit('.', 1)[1].lower()

def upload_profile_photo(user, profile_photo):
    if not allowed_file(profile_photo.filename):
        return False
    # generate a new name for file
    new_filename = generate_new_filename(profile_photo.filename)
    # upload to S3 bucket
    s3.Bucket(PROFILE_PHOTO_BUCKET_NAME).upload_fileobj(profile_photo, new_filename)
    # Add file to db
    file = File(original_filename=profile_photo.filename, filename=new_filename, bucket=PROFILE_PHOTO_BUCKET_NAME, region="eu-west-2")
    db.session.add(file)
    db.session.commit()
    user.profile_photo_id = file.id
    db.session.commit()

def delete_profile_photo(file_id):
    try:
        file = File.query.filter_by(id=file_id).first()
        obj = s3.Object(PROFILE_PHOTO_BUCKET_NAME, file.filename)
        obj.delete()
    except AttributeError:
        return "Did not work"

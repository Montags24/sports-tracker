from app import app, db
from app.models import User, Sport

def reset_users():
    with app.app_context():
        users = User.query.all()

        for user in users:
            user.sport_id = None
            user.sign_up_timestamp = None
            user.attended_sport = False
            user.nominal_submitted = False
        db.session.commit()

if __name__ == "__main__":
    reset_users()
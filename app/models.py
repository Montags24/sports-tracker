from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    rank = db.Column(db.String(32))
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    company = db.Column(db.String(32))
    platoon = db.Column(db.Integer)
    section = db.Column(db.Integer)
    sport_id = db.Column(db.Integer, db.ForeignKey("sports.id"))
    sign_up_timestamp = db.Column(db.DateTime, index=True)
    attended_sport = db.Column(db.Boolean, default=False)

    roles = db.relationship("Role", secondary="user_roles")
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    def __repr__(self):
        return "<User {}>".format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def add_roles(self, username, roles):
        user = User.query.filter_by(username=username).first()
        # Roles in form of dictionary {'admin': False, 'sport_oic':True, 'staff': True}
        for role, bool in roles.items():
            role = Role.query.filter_by(name=role).first()
            user_role = UserRoles.query.filter_by(user_id=user.id, role_id=role.id).first()
            if bool:
                # Add role to user if user previously did not have it
                if not user_role:
                    user_role = UserRoles(user_id=user.id, role_id=role.id)
                    db.session.add(user_role)
                    db.session.commit()
            else:
                # Remove role from user
                if user_role:
                    UserRoles.query.filter_by(user_id=user.id, role_id=role.id).delete()
                    db.session.commit()
    
    def get_permissions(self):
        return [role.name for role in self.roles]
    
    def sign_up_to_sport(self, sport_name):
        sport = Sport.query.filter_by(name=sport_name.lower()).first()
        if sport:
            self.sport = sport
            self.sign_up_timestamp = datetime.now()
            db.session.commit()

    def unsign_up_to_sport(self, sport_name):
        sport = Sport.query.filter_by(name=sport_name.lower()).first()
        if self.sport_id == sport.id:
            self.sport_id = None
            self.sign_up_timestamp = None
            db.session.commit()


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return "<Role {}>".format(self.name)


class UserRoles(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Sport(db.Model):
    __tablename__ = "sports"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    description = db.Column(db.String(140))
    sport_oic = db.Column(db.String(32))
    sport_oic_email = db.Column(db.String(64))
    img_src = db.Column(db.String(256))
    capacity = db.Column(db.Integer)
    location = db.Column(db.String(64))
    timing = db.Column(db.String(32))
    users = db.relationship("User", backref="sport")

    def __repr__(self):
        return "<Sport {}>".format(self.name)
    
    def get_user_sign_ups(self):
        user_sign_ups = User.query.filter_by(sport_id=self.id).all()
        return len(user_sign_ups)
        
        
# Keep track of logged in user
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
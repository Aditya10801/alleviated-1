from hack import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String(64),index=True)
    password = db.Column(db.String)
    blogs = db.relationship('BlogPost')

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thumbnail = db.Column(db.String(255))
    title = db.Column(db.String(255))
    short_desc = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)
    content = db.Column(db.Text)
    author = db.Column(db.String, db.ForeignKey('user.username'))
    category = db.Column(db.String)
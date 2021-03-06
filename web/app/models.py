from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(60))
    occupation = db.Column(db.String(64))
    confirmed = db.Column(db.Boolean, default=False)
    sendEmail = db.Column(db.Boolean, default=False)
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiraton=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiraton)
        return s.dumps({'confirm':self.user_id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('confirm') != self.user_id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username

class Movie(db.Model):
    __tablename__='movies'

    movie_id = db.Column(db.Integer,primary_key=True)
    movie_name = db.Column(db.String(64),  index=True)
    movie_genres = db.Column(db.String(64))
    ratings = db.relationship('Rating', backref='movie', lazy='dynamic')

    def __repr__(self):
        return '<Movie %r>' % self.movie_name

class Rating(db.Model):

    __tablename__='ratings'

    # id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), primary_key=True)
    rating = db.Column(db.Integer)

    def __repr__(self):
        return '<Rating %r>' % self.rating

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
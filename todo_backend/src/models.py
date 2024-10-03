from . import db
import datetime
import jwt

SECRET_KEY = 'demo'

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128), nullable=False)
	email = db.Column(db.String(), unique=True, nullable=False)
	password_hash = db.Column(db.String())

	tasks = db.relationship('Task', backref='user')

class Task(db.Model):
	__tablename__ = 'tasks'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128), nullable=False)
	description = db.Column(db.String(1024), nullable=True)
	deadline = db.Column(db.DateTime, nullable=True)
	completed = db.Column(db.Boolean, default=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class JWTBlacklist(db.Model):

	__tablename__ = 'jwt_blacklist'

	id = db.Column(db.Integer, primary_key = True)
	token = db.Column(db.String(500), unique=True, nullable=False)
	blacklisted_on = db.Column(db.DateTime, nullable=False)

	def __init__(self, token):
		self.token = token
		self.blacklisted_on = datetime.datetime.now()

	def __repr__(self):
		return f'<id: token: {self.token}'
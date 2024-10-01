from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    lastLoggedIn = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username, email, role, password):
        self.username = username
        self.email = email
        self.role = role # Admin, manager, user
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')


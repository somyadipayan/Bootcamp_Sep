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

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    category_document_path = db.Column(db.String(80), nullable=False)
    products = db.relationship('Product', back_populates='category', cascade="all, delete-orphan")
    
    def __init__(self, name, category_document_path):
        self.name = name
        self.category_document_path = category_document_path

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', back_populates='products')
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref='products')

    def __init__(self, name, price, category_id, creator_id, unit, quantity):
        self.name = name
        self.price = price
        self.category_id = category_id
        self.creator_id = creator_id
        self.unit = unit
        self.quantity = quantity
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

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

class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='shopping_carts')
    cart_items = db.relationship('CartItems', back_populates='shopping_cart', cascade="all, delete-orphan")

    def __init__(self, user_id):
        self.user_id = user_id

class CartItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shopping_cart_id = db.Column(db.Integer, db.ForeignKey('shopping_cart.id'), nullable=False)
    shopping_cart = db.relationship('ShoppingCart', back_populates='cart_items')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='cart_items')
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, shopping_cart_id, product_id, quantity):
        self.shopping_cart_id = shopping_cart_id
        self.product_id = product_id
        self.quantity = quantity

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='orders')
    order_date = db.Column(db.DateTime, default=datetime.now)
    total_amount = db.Column(db.Float, nullable=False)

class OrderItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    order = db.relationship('Order', backref='order_items')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='order_items')
    quantity = db.Column(db.Integer, nullable=False)

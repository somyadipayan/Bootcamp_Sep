from flask import Flask, jsonify, request
from config import Config
from models import *
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

def create_admin():
    existing_admin = User.query.filter_by(role="admin").first()

    if existing_admin:
        return jsonify({"message":"Admin already exists"}), 200
    
    try:
        admin = User(username="admin", email="admin@store.com", role="admin", password="1")
        db.session.add(admin)
        db.session.commit()
        return jsonify({"message":"Admin created successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500


with app.app_context():
    db.create_all()
    create_admin()

CORS(app, supports_credentials=True)

# Testing routes
@app.route("/")
def hello():
    return "Hello World!"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    role = data.get("role")
    password = data.get("password")

    if not username or not email or not role or not password:
        return jsonify({"error":"All fields are required"}), 400
    
    existingUser = User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first()

    if existingUser:
        return jsonify({"error":"User already exists"}), 400
    
    try:
        user = User(username=username, email=email, role=role, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message":"User created successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
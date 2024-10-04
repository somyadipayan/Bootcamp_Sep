from flask import Flask, jsonify, request, send_file
from config import Config
from models import *
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config.from_object(Config)

# Initialising objects in 'app' context
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

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

# REGISTER API
@app.route("/register", methods=["POST"])
def register():
    # Collecting data from request
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

# LOGIN API
@app.route("/login", methods=["POST"])
def login():
    # Collecting data from request
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error":"All fields are required"}), 400
    
    user = User.query.filter_by(email=email).first()

    # Checking credentials
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error":"Invalid credentials"}), 401
    
    # Creating access token
    access_token = create_access_token(identity={
        "email":user.email,
        "role":user.role,
        "id":user.id
    })

    #updating last logged in time
    user.lastLoggedIn = datetime.now()
    db.session.commit()

    return jsonify({"message":"Login successful", "access_token":access_token}), 200


@app.route("/protected")
@jwt_required()
def protected():
    currentUser = get_jwt_identity()
    user = User.query.filter_by(id=currentUser["id"]).first()
    
    if user.role != "admin":
        return jsonify({"error":"Unauthorized"}), 401

    return f'Hey {user.username} you can access this resource', 200

@app.route("/getuserdata", methods=["GET"])
@jwt_required()
def getuserdata():
    currentUser = get_jwt_identity()
    user = User.query.filter_by(id=currentUser["id"]).first()

    if not user:
        return jsonify({"error":"User not found"}), 404

    user_data = {
        "id":user.id,
        "username":user.username,
        "email":user.email,
        "role":user.role
    }

    return jsonify({"message": "Found User", "user":user_data}), 200

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message":"Logout successful"})
    unset_jwt_cookies(response)
    return response, 200

import os

# CRUD ON CATEGORIES
@app.route("/category", methods=["POST"])
@jwt_required()
def create_category():
    # Restrcting this to only admins
    currentUser = get_jwt_identity()
    if currentUser["role"] != "admin" or currentUser["role"] != "manager":
        return jsonify({"error":"Unauthorized"}), 401

    name = request.form.get("name")
    pdf = request.files.get("pdf")

    if not name or not pdf:
        return jsonify({"error":"All fields are required"}), 400
    
    if pdf.filename == "":
        return jsonify({"error":"No file selected"}), 400

    existing_category = Category.query.filter_by(name=name).first()

    if existing_category:
        return jsonify({"error":"Category already exists"}), 400

    pdf_filename = secure_filename(name + ".pdf")
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    pdf.save(pdf_path)

    try:
        category = Category(name=name, category_document_path = pdf_filename)
        db.session.add(category)
        db.session.commit()
        return jsonify({"message":"Category created successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500
    
# Read all categories
@app.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    categories_data = []
    for category in categories:
        categories_data.append({
            "id":category.id,
            "name":category.name,
            "pdf":category.category_document_path
        })
    return jsonify({"categories":categories_data}), 200

# Read categories that are approved

# Read a category
@app.route("/category/<int:id>", methods=["GET"])
def get_category(id):
    category = Category.query.filter_by(id=id).first()
    if not category:
        return jsonify({"error":"Category not found"}), 404
    category_data = {
        "id":category.id,
        "name":category.name,
        "pdf":category.category_document_path
    }
    return jsonify({"category":category_data}), 200 


# Update/Edit a category
@app.route("/category/<int:id>", methods=["PUT"]) 
@jwt_required()
def update_category(id):
    # Restrcting this to only admins
    currentUser = get_jwt_identity()
    if currentUser["role"] != "admin":
        return jsonify({"error":"Unauthorized"}), 401

    name = request.form.get("name")
    pdf = request.files.get("pdf")
    
    category = Category.query.filter_by(id=id).first()

    if not category:
        return jsonify({"error":"Category not found"}), 404

    if pdf:
        pdf_filename = secure_filename(name + ".pdf")
        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_filename)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        pdf.save(pdf_path)
        category.category_document_path = pdf_filename

    if not (name == ""):
        category.name = name

    try:
        db.session.commit()
        return jsonify({"message":"Category updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500
    

# Delete a category
@app.route("/category/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_category(id):
    # Restrcting this to only admins
    currentUser = get_jwt_identity()
    if currentUser["role"] != "admin":
        return jsonify({"error":"Unauthorized"}), 401
    
    category = Category.query.filter_by(id=id).first()

    if not category:
        return jsonify({"error":"Category not found"}), 404

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message":"Category deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500

@app.route("/view-catalogue/<int:id>", methods=["GET"])
def view_catalogue(id):
    category = Category.query.filter_by(id=id).first()
    if not category:
        return jsonify({"error":"Category not found"}), 404
    pdf = category.category_document_path
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf)
    return send_file(pdf_path, as_attachment=False)


if __name__ == "__main__":
    app.run(debug=True)
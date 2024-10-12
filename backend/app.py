from flask import Flask, jsonify, request, send_file, Response
from config import Config
from models import *
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from werkzeug.utils import secure_filename
from tools import workers, task, mailer
import os
import matplotlib.pyplot as plt
import io
import csv
from flask_caching import Cache


app = Flask(__name__)
app.config.from_object(Config)

# Initialising objects in 'app' context
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
cache = Cache(app)
mailer.init_app(app)

# Configuring Celery
celery = workers.celery
celery.conf.update(
    broker_url=app.config["CELERY_BROKER_URL"],
    result_backend=app.config["CELERY_RESULT_BACKEND"],
)

celery.Task = workers.ContextTask

app.app_context().push()

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
    mailer.send_email("fXb7v@example.com", "Test", "Hello World")
    # result = task.sendHi.delay(1)
    # print(result.get())
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
    if currentUser["role"] != "admin":
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
@cache.cached(timeout=600)
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

# CRUD on PRODUCTS
# Manager and Admin
@app.route('/product', methods=['POST'])
@jwt_required()
def create_product():
    this_user = get_jwt_identity()
    if this_user["role"] == "user":
        return {"error": "Unauthorized"}, 401
    
    data = request.json
    name = data["name"]
    unit = data["unit"]
    price = data["price"]
    quantity = data["quantity"]
    category_id = data["category_id"]

    if not name or not unit or not price or not quantity:
        return {"error": "Required Fields Missing"}, 400
    if quantity <= 0:
        return {"error": "Quantity must be greater than 0"}, 400
    if price <= 0:
        return {"error": "Rate per unit must be greater than 0"}, 400
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return {"error": "Category not found"}, 404
    new_product = Product(name=name,
                          unit=unit,
                          price=price,
                          quantity=quantity,
                          category_id=category_id,
                          creator_id=this_user["id"])
    try:
        db.session.add(new_product)
        db.session.commit()
        return {"message": "Product created successfully"}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to create product"}, 500
# Get all products in a category
@app.route('/category/<int:id>/products', methods=['GET'])
def get_products_by_category(id):
    products = Product.query.filter_by(category_id=id).all()
    products_data = []
    for product in products:
        products_data.append({
            "id":product.id,
            "name":product.name,
            "unit":product.unit,
            "price":product.price,
            "quantity":product.quantity,
            "category_id":product.category_id,
            "creator_email":product.creator_email
        })
    return jsonify(products_data), 200

# GET ALL PRODUCTS
@app.route('/products', methods=['GET'])
def get_products():
    categories = Category.query.all()
    data = []
    for category in categories:
        products = []
        for product in category.products:
            products.append({
                "id":product.id,
                "name":product.name,
                "unit":product.unit,
                "price":product.price,
                "quantity":product.quantity,
            })
        data.append({
            "id":category.id,
            "name":category.name,
            "pdf":category.category_document_path,
            "products":products
        })
    return jsonify(data), 200


# GET SINGLE PRODUCT BY IT'S ID
@app.route('/product/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.filter_by(id=id).first()
    if not product:
        return {"error": "Product not found"}, 404
    product_data = []
    product_data.append({
        "id":product.id,
        "name":product.name,
        "unit":product.unit,
        "price":product.price,
        "quantity":product.quantity,
        "category_id":product.category_id,
        "creator_email":product.creator_email
    })
    return jsonify(product_data), 200


# UPDATE PRODUCT
@app.route('/product/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    this_user = get_jwt_identity()
    if this_user["role"] == "user":
        return {"error": "Unauthorized"}, 401
    data = request.json
    name = data["name"]
    unit = data["unit"]
    price = data["price"]
    quantity = data["quantity"]
    if not name or not unit or not price or not quantity:
        return {"error": "Required Fields Missing"}, 400
    if quantity <= 0:
        return {"error": "Quantity must be greater than 0"}, 400
    if price <= 0:
        return {"error": "Rate per unit must be greater than 0"}, 400
    product = Product.query.filter_by(id=id).first()
    if not product:
        return {"error": "Product not found"}, 404
    product.name = name
    product.unit = unit
    product.price = price
    product.quantity = quantity
    try:
        db.session.commit()
        return {"message": "Product updated successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to update product"}, 500

 # DELETE PRODUCT   
@app.route('/product/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    this_user = get_jwt_identity()
    if this_user["role"] == "user":
        return {"error": "Unauthorized"}, 401
    product = Product.query.filter_by(id=id).first()
    if not product:
        return {"error": "Product not found"}, 404
    try:
        db.session.delete(product)
        db.session.commit()
        return {"message": "Product deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to delete product"}, 500

@app.route("/add-to-cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return {"error": "You are not supposed to do this!"}, 401
    data = request.json
    product_id = data["product_id"]
    quantity = data["quantity"]
    if not product_id or not quantity:
        return {"error": "Required Fields Missing"}, 400
    if quantity <= 0:
        return {"error": "Quantity must be greater than 0"}, 400
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return {"error": "Product not found"}, 404
    if product.quantity < quantity:
        return {"error": "Insufficient quantity"}, 400
    
    # Checking if the user already has a cart
    user_cart = ShoppingCart.query.filter_by(user_id=this_user["id"]).first()

    if not user_cart:
        user_cart = ShoppingCart(user_id=this_user["id"])
        try:
            db.session.add(user_cart)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": "Failed to add product to cart"}, 500

    cart_item = CartItems.query.filter_by(shopping_cart_id=user_cart.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItems(shopping_cart_id=user_cart.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    try:
        db.session.commit()
        return {"message": "Product added to cart successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to add product to cart"}, 500

@app.route("/view-cart", methods=["GET"])
@jwt_required()
def view_cart():
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return {"error": "You are not supposed to do this!"}, 401
    user_cart = ShoppingCart.query.filter_by(user_id=this_user["id"]).first()
    if not user_cart:
        return {"error": "Cart not found"}, 404
    cart_data = []
    for cart_item in user_cart.cart_items:
        cart_data.append({
            "id": cart_item.id,
            "product_id": cart_item.product_id,
            "product_name": cart_item.product.name,
            "unit": cart_item.product.unit,
            "price": cart_item.product.price,
            "quantity": cart_item.quantity,
            "total": cart_item.product.price * cart_item.quantity
        })
    return jsonify(cart_data), 200

@app.route("/update-cart", methods=["POST"])
@jwt_required()
def update_cart():
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return {"error": "You are not supposed to do this!"}, 401
    data = request.json
    quantity = data["quantity"]
    product_id = data["product_id"]
    if not quantity:
        return {"error": "Required Fields Missing"}, 400
    if quantity <= 0:
        return {"error": "Quantity must be greater than 0"}, 400
    user_cart = ShoppingCart.query.filter_by(user_id=this_user["id"]).first()
    if not user_cart:
        return {"error": "Cart not found"}, 404
    cart_item = CartItems.query.filter_by(shopping_cart_id=user_cart.id, product_id=product_id).first()
    if not cart_item:
        return {"error": "Product not found in cart"}, 404
    cart_item.quantity = quantity
    try:
        db.session.commit()
        return {"message": "Cart updated successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to update cart"}, 500

@app.route("/remove-from-cart", methods=["POST"])
@jwt_required()
def remove_from_cart():
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return {"error": "You are not supposed to do this!"}, 401
    data = request.json
    product_id = data["product_id"]
    user_cart = ShoppingCart.query.filter_by(user_id=this_user["id"]).first()
    if not user_cart:
        return {"error": "Cart not found"}, 404
    cart_item = CartItems.query.filter_by(shopping_cart_id=user_cart.id, product_id=product_id).first()
    if not cart_item:
        return {"error": "Product not found in cart"}, 404
    try:
        db.session.delete(cart_item)
        db.session.commit()
        return {"message": "Product removed from cart successfully"}, 200
    except Exception as e:
        db.session.rollback()

@app.route("/place-order", methods=["POST"])
@jwt_required()
def place_order():
    this_user = get_jwt_identity()
    if this_user["role"] != "user":
        return {"error": "You are not supposed to do this!"}, 401
    user_cart = ShoppingCart.query.filter_by(user_id=this_user["id"]).first()
    if not user_cart or not user_cart.cart_items:
        return {"error": "Cart is empty"}, 404
    order_items = []
    total_amount = 0
    for item in user_cart.cart_items:
        if item.quantity > item.product.quantity:
            return {"error": "Insufficient quantity"}, 400
        total_amount += item.product.price * item.quantity
        order_item = OrderItems(product_id=item.product_id, quantity=item.quantity)
        order_items.append(order_item)
        item.product.quantity -= item.quantity
    new_order = Order(user_id=this_user["id"], order_items=order_items, total_amount=total_amount)
    try:
        db.session.add(new_order)
        db.session.delete(user_cart)
        db.session.commit()
        return {"message": "Order placed successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to place order: {str(e)}"}, 500
    
# ADMIN DASHBOARD
# Graphs, CSV Reports, etc.
#
@app.route('/order-history-report', methods=['GET'])
@jwt_required()
def order_history_report():
    this_user = get_jwt_identity()
    if this_user["role"] != "admin":
        return {"error": "You are not supposed to do this!"}, 401
    orders = Order.query.all()
    total_orders = len(orders)
    total_amount = sum(order.total_amount for order in orders)
    total_items = sum(len(order.order_items) for order in orders)

    order_dates = [order.order_date.strftime('%Y-%m-%d') for order in orders]
    order_counts = {date: order_dates.count(date) for date in set(order_dates)}

    plt.figure(figsize=(10, 6))
    plt.bar(order_counts.keys(), order_counts.values())
    plt.xlabel('Date')
    plt.ylabel('Number of Orders')
    plt.title('Order History Report')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return jsonify({
        'total_orders': total_orders,
        'total_amount': total_amount,
        'total_items': total_items
    })
  
@app.route('/order-history-report-graph', methods=['GET'])
def order_history_report_graph():
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/order-category-pie-chart', methods=['GET'])
def order_category_pie_chart():

    orders = Order.query.all()

    category_counts = {}
    for order in orders:
        for item in order.order_items:
            category_name = item.product.category.name
            if category_name not in category_counts:
                category_counts[category_name] = 0
            category_counts[category_name] += item.quantity

    plt.figure(figsize=(10, 6))
    plt.pie(category_counts.values(), labels=category_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Orders from Different Categories')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')

def generate_csv_report():
    orders = Order.query.all()
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)

    # Write header row
    csv_writer.writerow(['Order ID','Order Date', 'User Name', 'Total Amount'])

    # Write order details
    for order in orders:
        csv_writer.writerow([order.id, order.order_date.strftime('%Y-%m-%d'), order.user.username, order.total_amount])
    return csv_buffer.getvalue()

@app.route('/download-order-csv', methods=['GET'])
def download_order_csv():
    csv_data = generate_csv_report()
    return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=orders.csv'})

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    cache.clear()
    return jsonify({'message': 'Cache cleared successfully'}), 200

if __name__ == "__main__":
    app.run(debug=True)
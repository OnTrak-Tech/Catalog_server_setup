# app.py
# Secure Flask application with JWT authentication, bcrypt password hashing, and PostgreSQL database
# Requirements:
# pip install Flask Flask-SQLAlchemy Flask-JWT-Extended Flask-Bcrypt psycopg2-binary pyOpenSSL

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import timedelta
import os
import secrets

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://catalog_user:catalog_pass@localhost:5432/catalog"

# 1. Strong JWT secret key from environment variable
# Generate a strong key if not set in environment
if not os.environ.get("JWT_SECRET_KEY"):
    print("WARNING: JWT_SECRET_KEY not set in environment. Using auto-generated key.")
    print("For production, set a permanent JWT_SECRET_KEY environment variable.")
    
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", secrets.token_hex(32))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)  # Initialize bcrypt for password hashing

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    
    user = User.query.filter_by(username=username).first()
    
    # 2. Using bcrypt to check password
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route("/products", methods=["GET"])
@jwt_required(optional=True)
def get_products():
    current_user = get_jwt_identity()
    products = Product.query.all()
    return jsonify([{"id": p.id, "name": p.name, "description": p.description, "price": p.price} for p in products])

@app.route("/admin/products", methods=["POST"])
@jwt_required()
def add_product():
    current_user = get_jwt_identity()
    data = request.json
    
    new_product = Product(
        name=data.get("name"),
        description=data.get("description"),
        price=data.get("price")
    )
    
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify({"msg": "Product added", "id": new_product.id}), 201

# Initialize database and add sample data
def initialize_database():
    with app.app_context():
        db.create_all()
        
        # Check if we already have users
        if User.query.count() == 0:
            # Add a default admin user with hashed password
            hashed_password = bcrypt.generate_password_hash("secure_password").decode('utf-8')
            admin_user = User(username="admin", password=hashed_password)
            db.session.add(admin_user)
            db.session.commit()
        
        # Check if we already have products
        if Product.query.count() == 0:
            # Add sample products
            sample_products = [
                Product(name="Laptop", description="High-performance laptop", price=999.99),
                Product(name="Smartphone", description="Latest model smartphone", price=699.99),
                Product(name="Headphones", description="Noise-cancelling headphones", price=199.99)
            ]
            db.session.add_all(sample_products)
            db.session.commit()

if __name__ == "__main__":
    # Initialize the database
    initialize_database()
    
    # For development, use adhoc certificates
    if os.environ.get("FLASK_ENV") == "development":
        app.run(host="0.0.0.0", port=5000, ssl_context="adhoc")
    else:
        # 3. For production, use Let's Encrypt certificates
        # Assuming certificates are stored in standard locations
        cert_path = "/etc/letsencrypt/live/yourdomain.com/fullchain.pem"
        key_path = "/etc/letsencrypt/live/yourdomain.com/privkey.pem"
        
        if os.path.exists(cert_path) and os.path.exists(key_path):
            app.run(host="0.0.0.0", port=5000, ssl_context=(cert_path, key_path))
        else:
            print("WARNING: Let's Encrypt certificates not found. Using adhoc certificates.")
            print("For production, install Let's Encrypt certificates.")
            app.run(host="0.0.0.0", port=5000, ssl_context="adhoc")
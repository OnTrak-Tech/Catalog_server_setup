# app.py
# Secure Flask application with JWT authentication, bcrypt password hashing, and PostgreSQL database
# Requirements:
# pip install Flask Flask-SQLAlchemy Flask-JWT-Extended Flask-Bcrypt psycopg2-binary pyOpenSSL

from flask import Flask, jsonify, render_template, request, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import timedelta
import os
import secrets
import logging
import traceback

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://catalog_user:catalog_pass@localhost:5432/catalog"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    image_url = db.Column(db.String(255), default="default-product.jpg")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route("/login", methods=["POST"])
def login():
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
            
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        
        if not username or not password:
            return jsonify({"msg": "Missing username or password"}), 400
        
        user = User.query.filter_by(username=username).first()
        
        # 2. Using bcrypt to check password
        if not user or not bcrypt.check_password_hash(user.password, password):
            return jsonify({"msg": "Invalid credentials"}), 401
        
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"msg": "Server error during login"}), 500

@app.route("/products", methods=["GET"])
@jwt_required(optional=True)
def get_products():
    try:
        current_user = get_jwt_identity()
        products = Product.query.all()
        return jsonify([{
            "id": p.id, 
            "name": p.name, 
            "description": p.description, 
            "price": p.price,
            "image_url": f"/static/images/products/{p.image_url}"
        } for p in products])
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"msg": "Error fetching products"}), 500

@app.route("/admin/products", methods=["POST"])
@jwt_required()
def add_product():
    try:
        current_user = get_jwt_identity()
        
        # Handle form data with file upload
        if request.content_type and 'multipart/form-data' in request.content_type:
            if 'name' not in request.form or 'price' not in request.form:
                return jsonify({"msg": "Missing required product data"}), 400
            
            name = request.form.get('name')
            description = request.form.get('description', '')
            price = float(request.form.get('price'))
            
            # Handle image upload
            image_filename = "default-product.jpg"
            if 'image' in request.files:
                image = request.files['image']
                if image.filename:
                    # Secure the filename
                    image_filename = f"{secrets.token_hex(8)}_{image.filename}"
                    image_path = os.path.join('static/images/products', image_filename)
                    image.save(image_path)
            
            new_product = Product(
                name=name,
                description=description,
                price=price,
                image_url=image_filename
            )
        
        # Handle JSON data (no file upload)
        elif request.is_json:
            data = request.json
            
            if not data.get("name") or not data.get("price"):
                return jsonify({"msg": "Missing required product data"}), 400
            
            new_product = Product(
                name=data.get("name"),
                description=data.get("description", ""),
                price=float(data.get("price")),
                image_url=data.get("image_url", "default-product.jpg")
            )
        
        else:
            return jsonify({"msg": "Unsupported content type"}), 400
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            "msg": "Product added", 
            "id": new_product.id,
            "image_url": f"/static/images/products/{new_product.image_url}"
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding product: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"msg": "Server error while adding product"}), 500

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
                Product(name="Laptop", description="High-performance laptop with the latest processor, 16GB RAM, and 512GB SSD storage. Perfect for work and gaming.", price=999.99, image_url="laptop.jpg"),
                Product(name="Smartphone", description="Latest model smartphone with 6.5-inch display, 128GB storage, and an amazing camera system.", price=699.99, image_url="smartphone.jpg"),
                Product(name="Headphones", description="Premium noise-cancelling headphones with 30-hour battery life and superior sound quality.", price=199.99, image_url="headphones.jpg"),
                Product(name="Smartwatch", description="Track your fitness, receive notifications, and more with this stylish and functional smartwatch.", price=249.99, image_url="smartwatch.jpg"),
                Product(name="Tablet", description="Lightweight tablet with 10-inch display, perfect for entertainment and productivity on the go.", price=349.99, image_url="tablet.jpg")
            ]
            db.session.add_all(sample_products)
            db.session.commit()

# Error handler for all routes
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({"msg": "Internal server error"}), 500

# CORS support
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    # Initialize the database
    try:
        initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        logger.error(traceback.format_exc())
    
    # For development, use adhoc certificates
    if os.environ.get("FLASK_ENV") == "development":
        app.run(host="0.0.0.0", port=5000, ssl_context="adhoc", debug=True)
    else:
        # 3. For production, use Let's Encrypt certificates
        # Assuming certificates are stored in standard locations
        cert_path = "/etc/letsencrypt/live/yourdomain.com/fullchain.pem"
        key_path = "/etc/letsencrypt/live/yourdomain.com/privkey.pem"
        
        if os.path.exists(cert_path) and os.path.exists(key_path):
            app.run(host="0.0.0.0", port=5000, ssl_context=(cert_path, key_path))
        else:
            logger.warning("Let's Encrypt certificates not found. Using adhoc certificates.")
            app.run(host="0.0.0.0", port=5000, ssl_context="adhoc")
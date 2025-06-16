# E-Commerce Catalog

A secure Flask application with JWT authentication, product catalog, and admin features.

## Setup Instructions

1. Make sure PostgreSQL is installed and running
2. Create a database and user:
   ```sql
   CREATE DATABASE catalog;
   CREATE USER catalog_user WITH PASSWORD 'catalog_pass';
   GRANT ALL PRIVILEGES ON DATABASE catalog TO catalog_user;
   ```

3. Install dependencies:
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-JWT-Extended Flask-Bcrypt psycopg2-binary pyOpenSSL
   ```

4. Run the database migration script:
   ```bash
   ./migrate_db.py
   ```

5. Start the application:
   ```bash
   python app.py
   ```

## Features

- Secure user authentication with JWT
- Product catalog with images
- Admin interface for adding products
- HTTPS support
- Responsive e-commerce UI

## Default Admin Credentials

- Username: admin
- Password: secure_password

## API Endpoints

- `GET /products` - Get all products
- `POST /login` - Authenticate user
- `POST /admin/products` - Add a new product (requires authentication)
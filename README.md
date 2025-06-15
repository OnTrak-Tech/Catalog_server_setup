# Secure Product Catalog

A secure web application for managing and displaying product information with JWT authentication, HTTPS, and PostgreSQL database.

## Features

- **Secure Authentication**: JWT-based authentication system
- **Password Security**: Bcrypt password hashing
- **HTTPS Support**: SSL/TLS encryption with Let's Encrypt integration
- **Database**: PostgreSQL for reliable data storage
- **Responsive UI**: Clean, mobile-friendly interface
- **Role-Based Access**: Public product viewing with protected admin features

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Authentication**: Flask-JWT-Extended
- **Password Security**: Flask-Bcrypt
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **HTTPS**: PyOpenSSL with Let's Encrypt support

## Installation

### Prerequisites

- Python 3.7+
- PostgreSQL
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/secure-product-catalog.git
   cd secure-product-catalog
   ```

2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install Flask Flask-SQLAlchemy Flask-JWT-Extended Flask-Bcrypt psycopg2-binary pyOpenSSL
   ```

4. Set up PostgreSQL:
   ```sql
   CREATE DATABASE catalog;
   CREATE USER catalog_user WITH PASSWORD 'catalog_pass';
   GRANT ALL PRIVILEGES ON DATABASE catalog TO catalog_user;
   ```

5. Configure environment variables (recommended for production):
   ```
   export JWT_SECRET_KEY=$(openssl rand -hex 32)
   export FLASK_ENV=production
   ```

## Running the Application

### Development Mode

```
python app.py
```

The application will be available at https://localhost:5000 with a self-signed certificate.

### Production Mode

1. Install Let's Encrypt certificates:
   ```
   sudo apt-get update
   sudo apt-get install certbot
   sudo certbot certonly --standalone -d yourdomain.com
   ```

2. Update the certificate paths in app.py if needed:
   ```python
   cert_path = "/etc/letsencrypt/live/yourdomain.com/fullchain.pem"
   key_path = "/etc/letsencrypt/live/yourdomain.com/privkey.pem"
   ```

3. Run the application:
   ```
   python app.py
   ```

## Usage

### Public Access
- Visit the homepage to view all products
- No authentication required for viewing products

### Admin Access
1. Click "Admin Login" button
2. Login with default credentials:
   - Username: admin
   - Password: secure_password
3. After login, you can:
   - Add new products
   - View all products

## Security Features

### JWT Authentication
- Tokens expire after 1 hour
- Protected routes for admin functions

### Password Security
- Passwords are hashed using bcrypt
- Plain text passwords are never stored

### HTTPS
- All traffic is encrypted using SSL/TLS
- Development mode uses self-signed certificates
- Production mode uses Let's Encrypt certificates

### Database Security
- Parameterized queries prevent SQL injection
- Dedicated database user with limited permissions

## Project Structure

```
secure-product-catalog/
├── app.py                 # Main application file
├── templates/
│   └── index.html         # Frontend template
├── static/
│   └── favicon.ico        # Site favicon
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## API Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/` | GET | No | Main page with product listing |
| `/login` | POST | No | Authenticate and get JWT token |
| `/products` | GET | No | Get all products |
| `/admin/products` | POST | Yes | Add a new product |

## Future Enhancements

- Product image upload
- Product categories
- User registration
- Product editing and deletion
- Order management
- Admin dashboard

## License

MIT

## Author

Gideon Adjei

---

*This project was created as a demonstration of secure web application development practices.*
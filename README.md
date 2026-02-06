# Congo - Amazon Clone

A full-stack e-commerce application built with Python (Flask), HTML/Tailwind CSS, and PostgreSQL.

## Features

- User authentication (register, login, logout)
- Product browsing and search
- Shopping cart functionality
- Order management
- Category filtering
- Responsive design with Tailwind CSS

## Tech Stack

- **Backend**: Python 3.x, Flask, SQLAlchemy
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Database**: PostgreSQL
- **Other**: Flask-CORS, python-dotenv

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd Congo
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**:
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE congo_db;
   
   # Exit psql
   \q
   ```

5. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and update the following:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: A random secret key for Flask sessions

6. **Initialize the database with sample data** (optional):
   ```bash
   python setup_db.py
   ```
   This will create all necessary tables and add sample products to get you started.

7. **Run the application**:
   ```bash
   python run.py
   ```

8. **Access the application**:
   - Open your browser and navigate to `http://127.0.0.1:5000`

## Project Structure

```
Congo/
├── backend/
│   ├── app/
│   │   └── __init__.py          # Flask app initialization
│   ├── api/
│   │   ├── products.py          # Product API endpoints
│   │   ├── users.py             # User authentication endpoints
│   │   ├── orders.py            # Order management endpoints
│   │   └── cart.py              # Shopping cart endpoints
│   └── models/
│       ├── user.py              # User model
│       ├── product.py           # Product model
│       ├── order.py             # Order models
│       └── cart.py              # Cart model
├── frontend/
│   ├── templates/               # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   └── products.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── database/
│   └── init.sql                 # Database initialization script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore
└── run.py                       # Application entry point
```

## API Endpoints

### Products
- `GET /api/products/` - Get all products (with optional filtering)
- `GET /api/products/<id>` - Get a single product
- `POST /api/products/` - Create a new product (admin)
- `GET /api/products/categories` - Get all categories

### Users
- `POST /api/users/register` - Register a new user
- `POST /api/users/login` - Login user
- `POST /api/users/logout` - Logout user
- `GET /api/users/me` - Get current user
- `GET /api/users/<id>` - Get user by ID

### Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/` - Add item to cart
- `PUT /api/cart/<id>` - Update cart item
- `DELETE /api/cart/<id>` - Remove item from cart

### Orders
- `GET /api/orders/` - Get user's orders
- `GET /api/orders/<id>` - Get a specific order
- `POST /api/orders/` - Create a new order from cart

## Development

To add sample data, you can use the Flask shell:

```bash
python -c "
from backend.app import create_app, db
from backend.models.product import Product

app = create_app()
with app.app_context():
    # Add sample products
    products = [
        Product(name='Laptop', description='High-performance laptop', price=999.99, stock=50, category='Electronics'),
        Product(name='Headphones', description='Wireless headphones', price=199.99, stock=100, category='Electronics'),
        Product(name='Coffee Maker', description='Programmable coffee maker', price=79.99, stock=30, category='Home & Kitchen'),
    ]
    for p in products:
        db.session.add(p)
    db.session.commit()
    print('Sample products added!')
"
```

## License

This project is for educational purposes.


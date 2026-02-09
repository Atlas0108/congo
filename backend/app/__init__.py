from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    template_dir = os.path.join(base_dir, "frontend", "templates")
    static_dir = os.path.join(base_dir, "frontend", "static")

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # Configuration
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    )

    # Database URL - check multiple environment variable names for compatibility
    database_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("POSTGRES_PRISMA_URL")
    )
    
    # In production (Vercel), require DATABASE_URL to be set
    if not database_url:
        if os.getenv("VERCEL") or os.getenv("FLASK_ENV") == "production":
            raise ValueError(
                "DATABASE_URL environment variable is required in production. "
                "Please set it in your Vercel project settings."
            )
        # Only use localhost default in development
        database_url = "postgresql+psycopg://localhost/congo_db"
        print("⚠️  Warning: Using default localhost database. Set DATABASE_URL for production.")

    # Convert postgresql:// to postgresql+psycopg:// for SQLAlchemy if needed
    if database_url.startswith("postgresql://") and "psycopg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Determine if this is a remote database (requires SSL) or local (no SSL)
    is_remote_db = any(
        host in database_url
        for host in [
            "neon.tech",
            "aws.neon.tech",
            "supabase.co",
            "railway.app",
            "render.com",
        ]
    )

    # Configure engine options based on database type
    engine_options = {
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 300,  # Recycle connections after 5 minutes
    }

    # Only require SSL for remote databases (Neon, Supabase, etc.)
    if is_remote_db:
        engine_options["connect_args"] = {"connect_timeout": 10, "sslmode": "require"}
    else:
        # Local database - no SSL required
        engine_options["connect_args"] = {"connect_timeout": 10, "sslmode": "disable"}

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register blueprints
    from backend.api import products, users, orders, cart, test_db

    app.register_blueprint(products.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(cart.bp)
    app.register_blueprint(test_db.bp)

    # Register frontend routes
    from flask import render_template, jsonify

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/products")
    def products_page():
        return render_template("products.html")

    @app.route("/product/<int:product_id>")
    def product_detail(product_id):
        return render_template("product_detail.html", product_id=product_id)

    @app.route("/cart")
    def cart_page():
        return render_template("cart.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    @app.route("/orders")
    def orders_page():
        return render_template("orders.html")

    @app.route("/account")
    def account_page():
        return render_template("account.html")

    @app.route("/account/addresses")
    def addresses_page():
        return render_template("addresses.html")

    @app.route("/account/addresses/new")
    def add_address_page():
        return render_template("add_address.html")

    @app.route("/account/payment-methods")
    def payment_methods_page():
        return render_template("payment_methods.html")

    @app.route("/account/security")
    def security_page():
        return render_template("security.html")

    @app.route("/about/local")
    def about_local_page():
        return render_template("about_local.html")

    @app.route("/merchant")
    def merchant_profile_page():
        return render_template("merchant_profile.html")

    @app.route("/merchant/onboard")
    def merchant_onboarding_page():
        return render_template("merchant_onboarding.html")

    @app.route("/added-to-cart")
    def added_to_cart_page():
        return render_template("added_to_cart.html")

    # Create tables (only if database is available, skip in serverless if connection fails)
    # In serverless, we'll initialize lazily to avoid startup crashes
    app.db_initialized = False

    def init_db():
        """Initialize database tables - called lazily when needed"""
        if app.db_initialized:
            return

        try:
            with app.app_context():
                # Try to connect to database first
                db.engine.connect()
                db.create_all()

                # Add new columns/tables for merchant system if they don't exist
                try:
                    from sqlalchemy import inspect, text

                    inspector = inspect(db.engine)

                    # Add role column to users table if it doesn't exist
                    try:
                        user_columns = [
                            col["name"] for col in inspector.get_columns("users")
                        ]
                        if "role" not in user_columns:
                            with db.engine.connect() as conn:
                                conn.execute(
                                    text(
                                        "ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'shopper'"
                                    )
                                )
                                conn.commit()
                            print("✓ Added role column to users table")
                    except Exception as e:
                        print(
                            f"Note: Could not add role column (may already exist): {e}"
                        )

                    # Add default_category column to users table if it doesn't exist
                    try:
                        user_columns = [
                            col["name"] for col in inspector.get_columns("users")
                        ]
                        if "default_category" not in user_columns:
                            with db.engine.connect() as conn:
                                conn.execute(
                                    text(
                                        "ALTER TABLE users ADD COLUMN default_category VARCHAR(100)"
                                    )
                                )
                                conn.commit()
                            print("✓ Added default_category column to users table")
                    except Exception as e:
                        print(
                            f"Note: Could not add default_category column (may already exist): {e}"
                        )

                    # Add merchant_id column to products table if it doesn't exist
                    try:
                        product_columns = [
                            col["name"] for col in inspector.get_columns("products")
                        ]
                        if "merchant_id" not in product_columns:
                            with db.engine.connect() as conn:
                                conn.execute(
                                    text(
                                        "ALTER TABLE products ADD COLUMN merchant_id INTEGER REFERENCES users(id)"
                                    )
                                )
                                conn.commit()
                            print("✓ Added merchant_id column to products table")
                    except Exception as e:
                        print(
                            f"Note: Could not add merchant_id column (may already exist): {e}"
                        )

                    # Create merchant_profiles table if it doesn't exist
                    if "merchant_profiles" not in inspector.get_table_names():
                        db.create_all()
                        print("✓ Created merchant_profiles table")
                except Exception as e:
                    # Tables might already exist
                    print(f"Note: Schema migration check completed: {e}")

                app.db_initialized = True
        except Exception as e:
            # Database connection failed - this is OK in serverless if DB isn't configured yet
            import traceback

            print(f"⚠️  Database initialization skipped: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            print(
                "   (This is normal if DATABASE_URL is not set or database is not accessible)"
            )

    # Only initialize DB if not in serverless environment (Vercel sets VERCEL env var)
    if not os.getenv("VERCEL"):
        # Local development - initialize immediately
        init_db()
    else:
        # Serverless - initialize on first request via a before_request hook
        @app.before_request
        def ensure_db_initialized():
            if not app.db_initialized:
                init_db()

    # Register error handlers to return JSON instead of HTML
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    return app

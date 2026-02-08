from backend.app import create_app, db
import os
import socket
import threading
import random
from dotenv import load_dotenv

load_dotenv()

app = create_app()

# Placeholder merchant data
MERCHANT_DATA = [
    {
        "business_name": "Local Goods Co.",
        "description": "Your neighborhood source for quality local products. We partner with local artisans and businesses to bring you the best.",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "phone": "+1-415-555-0101",
        "email": "info@localgoodsco.com",
        "website": "https://localgoodsco.com",
    },
    {
        "business_name": "Bay Area Marketplace",
        "description": "Supporting local businesses in the Bay Area. Fast shipping and excellent customer service.",
        "city": "Oakland",
        "state": "CA",
        "country": "USA",
        "phone": "+1-510-555-0202",
        "email": "hello@bayareamarketplace.com",
        "website": "https://bayareamarketplace.com",
    },
    {
        "business_name": "Community Store",
        "description": "Connecting you with amazing local products. Every purchase supports your community.",
        "city": "Berkeley",
        "state": "CA",
        "country": "USA",
        "phone": "+1-510-555-0303",
        "email": "contact@communitystore.com",
        "website": "https://communitystore.com",
    },
    {
        "business_name": "Golden Gate Goods",
        "description": "Premium products from local San Francisco businesses. Quality you can trust.",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "phone": "+1-415-555-0404",
        "email": "support@goldengategoods.com",
        "website": "https://goldengategoods.com",
    },
    {
        "business_name": "East Bay Essentials",
        "description": "Essential products from East Bay businesses. Fast, reliable, local.",
        "city": "Fremont",
        "state": "CA",
        "country": "USA",
        "phone": "+1-510-555-0505",
        "email": "info@eastbayessentials.com",
        "website": "https://eastbayessentials.com",
    },
    {
        "business_name": "Peninsula Products",
        "description": "Quality products from Peninsula businesses. Supporting local since 2020.",
        "city": "Palo Alto",
        "state": "CA",
        "country": "USA",
        "phone": "+1-650-555-0606",
        "email": "hello@peninsulaproducts.com",
        "website": "https://peninsulaproducts.com",
    },
    {
        "business_name": "North Bay Market",
        "description": "Your source for North Bay local products. Fresh, local, delivered.",
        "city": "Santa Rosa",
        "state": "CA",
        "country": "USA",
        "phone": "+1-707-555-0707",
        "email": "contact@northbaymarket.com",
        "website": "https://northbaymarket.com",
    },
    {
        "business_name": "Valley Vendors",
        "description": "Connecting Silicon Valley with quality local products. Innovation meets tradition.",
        "city": "San Jose",
        "state": "CA",
        "country": "USA",
        "phone": "+1-408-555-0808",
        "email": "info@valleyvendors.com",
        "website": "https://valleyvendors.com",
    },
]


def fetch_product_images_in_background():
    """Fetch images for products that don't have them (runs in background)"""
    try:
        from backend.utils.ensure_product_images import ensure_product_images

        with app.app_context():
            print("🖼️  Checking for products that need images...")
            updated = ensure_product_images()
            if updated > 0:
                print(f"✅ Updated {updated} products with images")
            else:
                print("✅ All products already have images")
    except Exception as e:
        print(f"⚠️  Warning: Could not fetch product images: {e}")


def ensure_merchants_in_background():
    """Ensure placeholder merchants exist and are assigned to products (runs in background)"""
    try:
        from backend.models.user import User
        from backend.models.merchant import MerchantProfile
        from backend.models.product import Product

        with app.app_context():
            print("🏪 Checking for merchants...")

            # Create merchants if they don't exist
            created_count = 0
            for merchant_data in MERCHANT_DATA:
                username = (
                    merchant_data["business_name"]
                    .lower()
                    .replace(" ", "_")
                    .replace(".", "")
                    .replace(",", "")
                )
                existing_user = User.query.filter_by(username=username).first()

                if existing_user:
                    continue

                # Create merchant user
                user = User(
                    username=username,
                    email=merchant_data["email"],
                    first_name=merchant_data["business_name"].split()[0],
                    last_name="Merchant",
                    phone=merchant_data["phone"].replace("-", "").replace("+1-", ""),
                    role="merchant",
                )
                user.set_password("merchant123")  # Default password

                db.session.add(user)
                db.session.flush()  # Get user.id

                # Create merchant profile
                address = f"{merchant_data['city']}, {merchant_data['state']} {merchant_data['country']}"
                merchant_profile = MerchantProfile(
                    user_id=user.id,
                    business_name=merchant_data["business_name"],
                    description=merchant_data["description"],
                    address=address,
                    city=merchant_data["city"],
                    state=merchant_data["state"],
                    country=merchant_data["country"],
                    phone=merchant_data["phone"],
                    email=merchant_data["email"],
                    website=merchant_data["website"],
                    is_verified=random.choice(
                        [True, True, False]
                    ),  # 2/3 chance of being verified
                    rating=round(random.uniform(3.5, 5.0), 1),
                    review_count=random.randint(10, 500),
                )

                db.session.add(merchant_profile)
                created_count += 1

            if created_count > 0:
                db.session.commit()
                print(f"✅ Created {created_count} new merchants")
            else:
                print("✅ All merchants already exist")

            # Assign merchants to products that don't have one
            merchants = User.query.filter_by(role="merchant").all()
            if merchants:
                products = Product.query.filter_by(merchant_id=None).all()
                if products:
                    assigned_count = 0
                    for product in products:
                        # Randomly assign a merchant (80% chance)
                        if random.random() < 0.8:
                            merchant = random.choice(merchants)
                            product.merchant_id = merchant.id
                            assigned_count += 1

                    if assigned_count > 0:
                        db.session.commit()
                        print(f"✅ Assigned merchants to {assigned_count} products")
    except Exception as e:
        print(f"⚠️  Warning: Could not ensure merchants: {e}")


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        if not is_port_in_use(port):
            return port
    return None


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    default_port = int(os.getenv("PORT", 5000))

    # Check if default port is available, if not find another
    if is_port_in_use(default_port):
        print(f"⚠️  Port {default_port} is already in use.")
        available_port = find_available_port(default_port)
        if available_port:
            print(f"✅ Using port {available_port} instead.")
            port = available_port
        else:
            print(
                f"❌ Could not find an available port. Please free up port {default_port} or set a different PORT in .env"
            )
            port = default_port
    else:
        port = default_port

    print(f"🚀 Starting Flask server on http://{host}:{port}")

    # Start image fetching in background thread (non-blocking)
    image_thread = threading.Thread(
        target=fetch_product_images_in_background, daemon=True
    )
    image_thread.start()

    # Start merchant population in background thread (non-blocking)
    merchant_thread = threading.Thread(
        target=ensure_merchants_in_background, daemon=True
    )
    merchant_thread.start()

    app.run(host=host, port=port, debug=True)

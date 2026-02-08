from backend.app import create_app
import os
import socket
from dotenv import load_dotenv

load_dotenv()

app = create_app()


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
    app.run(host=host, port=port, debug=True)

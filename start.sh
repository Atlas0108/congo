#!/bin/bash

# Congo E-commerce Startup Script
# This script sets up and runs the Flask application

set -e  # Exit on error

echo "🚀 Starting Congo E-commerce Application..."
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "✅ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql+psycopg://localhost/congo_db

# Flask Configuration
FLASK_APP=backend/app/__init__.py
FLASK_ENV=development
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Server Configuration
HOST=127.0.0.1
PORT=5000
EOF
    echo "✅ .env file created with default values"
    echo "⚠️  Please update DATABASE_URL in .env if your PostgreSQL setup differs"
fi

# Check if database exists (optional check)
echo ""
echo "💾 Database check..."
if command -v psql &> /dev/null; then
    # Try to check if database exists (this will fail gracefully if not)
    if psql -lqt | cut -d \| -f 1 | grep -qw congo_db 2>/dev/null; then
        echo "✅ Database 'congo_db' exists"
    else
        echo "⚠️  Database 'congo_db' not found. You may need to create it:"
        echo "   createdb congo_db"
    fi
else
    echo "⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed and configured."
fi

echo ""
echo "🎯 Starting Flask application..."
echo "📍 Server will be available at http://127.0.0.1:5000 (or next available port)"
echo "   Press Ctrl+C to stop the server"
echo ""

# Run the Flask application
python run.py


"""
Vercel serverless function entry point for Flask app
"""
import sys
import os
import traceback

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set environment to production for Vercel
os.environ.setdefault('FLASK_ENV', 'production')

# Create Flask app instance
# Wrap in try/except to handle initialization errors gracefully
try:
    from backend.app import create_app
    app = create_app()
except Exception as e:
    # If app creation fails, create a minimal app that shows the error
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    error_message = str(e)
    error_traceback = traceback.format_exc()
    
    @app.route('/')
    def error_handler():
        return jsonify({
            'error': 'Application initialization failed',
            'message': error_message,
            'traceback': error_traceback,
            'hint': 'Check DATABASE_URL environment variable and database connection'
        }), 500
    
    @app.route('/<path:path>')
    def catch_all(path):
        return error_handler()

# Vercel's @vercel/python builder automatically handles WSGI apps
# The app variable is exported and Vercel will use it directly


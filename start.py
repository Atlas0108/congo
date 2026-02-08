#!/usr/bin/env python3
"""
Congo E-commerce Startup Script
This script sets up and runs the Flask application automatically.
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def run_command(cmd, check=True, shell=False):
    """Run a shell command and return the result."""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def main():
    print("🚀 Starting Congo E-commerce Application...")
    print()
    
    # Get project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    venv_path = project_dir / "venv"
    venv_python = venv_path / "bin" / "python3"
    venv_pip = venv_path / "bin" / "pip"
    
    # Check if virtual environment exists
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        success, _, error = run_command([sys.executable, "-m", "venv", "venv"])
        if not success:
            print(f"❌ Failed to create virtual environment: {error}")
            sys.exit(1)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Install/upgrade dependencies
    print("📥 Installing dependencies...")
    
    # Upgrade pip first
    if sys.platform == "win32":
        pip_cmd = str(venv_path / "Scripts" / "pip.exe")
        python_cmd = str(venv_path / "Scripts" / "python.exe")
    else:
        pip_cmd = str(venv_pip)
        python_cmd = str(venv_python)
    
    run_command([pip_cmd, "install", "--quiet", "--upgrade", "pip"], check=False)
    
    # Install requirements
    success, _, error = run_command([pip_cmd, "install", "--quiet", "-r", "requirements.txt"])
    if not success:
        print(f"⚠️  Warning: Some dependencies may not have installed correctly: {error}")
    else:
        print("✅ Dependencies installed")
    
    # Check for .env file
    env_file = project_dir / ".env"
    if not env_file.exists():
        print("⚙️  Creating .env file...")
        secret_key = secrets.token_hex(32)
        env_content = f"""# Database Configuration
DATABASE_URL=postgresql+psycopg://localhost/congo_db

# Flask Configuration
FLASK_APP=backend/app/__init__.py
FLASK_ENV=development
SECRET_KEY={secret_key}

# Server Configuration
HOST=127.0.0.1
PORT=5000
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ .env file created with default values")
        print("⚠️  Please update DATABASE_URL in .env if your PostgreSQL setup differs")
    else:
        print("✅ .env file already exists")
    
    # Check database (optional)
    print()
    print("💾 Database check...")
    if sys.platform != "win32":
        # Try to check if psql is available
        success, _, _ = run_command(["which", "psql"], check=False)
        if success:
            # Try to check if database exists
            success, output, _ = run_command(["psql", "-lqt"], check=False)
            if success and "congo_db" in output:
                print("✅ Database 'congo_db' exists")
            else:
                print("⚠️  Database 'congo_db' not found. You may need to create it:")
                print("   createdb congo_db")
        else:
            print("⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed.")
    else:
        print("⚠️  Please ensure PostgreSQL is installed and configured.")
    
    print()
    print("🎯 Starting Flask application...")
    print("📍 Server will be available at http://127.0.0.1:5000 (or next available port)")
    print("   Press Ctrl+C to stop the server")
    print()
    
    # Run the Flask application
    run_file = project_dir / "run.py"
    try:
        os.execv(python_cmd, [python_cmd, str(run_file)])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()


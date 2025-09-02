#!/bin/bash

# Activate existing virtual environment
source venv/bin/activate

# Set SECRET_KEY environment variable
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Install dependencies (in case they're missing)
pip install flask flask_sqlalchemy bcrypt flask-wtf flask-limiter

# Run the Flask app
python app.py
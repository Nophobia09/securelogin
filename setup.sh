#!/bin/bash

# Activate existing virtual environment
source venv/bin/activate

# Set SECRET_KEY environment variable
export SECRET_KEY='46bf2e844a0462f3dbec446dacbe7645eff785cb53f096ef92c3a9e064598e22'

# Install dependencies (in case they're missing)
pip install flask flask_sqlalchemy bcrypt flask-wtf flask-limiter

# Run the Flask app
python app.py
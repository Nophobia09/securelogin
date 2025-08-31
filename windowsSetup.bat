@echo off

REM Activate the virtual environment
call venv\Scripts\activate

REM Set SECRET_KEY environment variable
set SECRET_KEY=a80d45e329b433b490a18dabe07234ae068e573961f8233a7765b0e07e0c9f23

REM Install dependencies (in case they're missing)
pip install flask flask_sqlalchemy bcrypt flask-wtf flask-limiter

REM Run the Flask app
python app.py
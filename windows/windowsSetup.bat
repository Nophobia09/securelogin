@echo off

REM Activate the virtual environment
call venv\Scripts\activate

REM Set SECRET_KEY environment variable
 for /f "delims=" %%a in ('python -c "import secrets; print(secrets.token_hex(32))"') do set SECRET_KEY=%%a

REM Install dependencies (in case they're missing)
pip install flask flask_sqlalchemy bcrypt flask-wtf flask-limiter

REM Run the Flask app
python app.py
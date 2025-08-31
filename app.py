from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
import bcrypt
import os
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '88b6a0dad1a9b5c53c9915ee093f833dd0934fa03e293f9b851721e0559c8f62') #fallback key incase of missing env variable
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    reset_token = db.Column(db.String(32), nullable=False)

class RegistrationForm(FlaskForm):
    username = StringField('Email or username', validators=[InputRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=128)])

class ForgotPasswordForm(FlaskForm):
    username = StringField('Email or username', validators=[InputRequired(), Length(min=4, max=80)])
    token = StringField('Reset token', validators=[InputRequired(), Length(min=32, max=32)])

@app.before_request
def create_tables():
    db.create_all()

@app.route('/forgotPass', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def forgot_password():
    form = ForgotPasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        token = form.token.data
        user = User.query.filter_by(username=username, reset_token=token).first()
        if user:
            flash("Token verified! You may now reset your password.", "success")
            return redirect(url_for('reset_password', username=username, token=token))
        else:
            flash("Invalid username or token.", "error")
        return redirect(url_for('forgot_password'))
    return render_template('forgotPass.html', form=form)

@app.route('/reset_password', methods=['GET', 'POST'])
@csrf.exempt
@limiter.limit("5 per minute")
def reset_password():
    username = request.args.get('username')
    token = request.args.get('token')
    user = User.query.filter_by(username=username, reset_token=token).first()
    form = RegistrationForm()
    if request.method == 'POST':
        password = request.form.get('password')
        reenter_password = request.form.get('reenter_password')
        if password and reenter_password and password == reenter_password:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user.password_hash = password_hash.decode('utf-8')
            db.session.commit()
            flash("Password has been reset! You may now log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Passwords do not match or are empty.", "error")
    return render_template('reset_password.html', form=form, username=username, token=token)

@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return redirect(url_for('signup_page'))
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        reset_token = secrets.token_hex(16)
        user = User(username=username, password_hash=password_hash.decode('utf-8'), reset_token=reset_token)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('show_token', token=reset_token))
    else:
        flash("Invalid input. Please check your entries.", "error")
        return redirect(url_for('signup_page'))

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        session['username'] = username
        flash("Login successful!", "success")
        return redirect(url_for('your_in'))
    else:
        flash("Invalid username or password.", "error")
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/show_token/<token>')
def show_token(token):
    return render_template('show_token.html', token=token)
    
@app.route('/index')
def login():
    form = RegistrationForm()
    return render_template('index.html', form=form)

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'username' not in session:
        flash("Please log in to access the home page.", "error")
        return redirect(url_for('login'))
    username = session['username']
    return render_template('home.html', username=username)

@app.route('/yourIn')
def your_in():
    if 'username' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    return render_template('yourIn.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    form = RegistrationForm()
    return render_template('signup.html', form=form)

@app.route('/user-agreement')
def user_agreement():
    return render_template('user-agreement.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) #debug=True for development if needed
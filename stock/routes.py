from flask import render_template, flash, url_for, redirect, request
from stock import app, db, bcrypt
from stock.forms import RegistrationForm, LoginForm, UpdateAccountForm, PortfolioForm
from stock.models import User, Portfolio
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
import secrets
import os
import email_validator
import yfinance as yf
import json

@app.route('/')
@app.route('/home')
def home():
    stocks = Portfolio.query.all()
    return render_template('home.html', stocks=stocks)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form=form)

@app.route('/login', methods = ['GET', 'POST'] )
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title = 'Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/portfolio/new', methods = ['GET', 'POST'])
@login_required
def portfolio():
    form = PortfolioForm()
    if form.validate_on_submit():
        stock = Portfolio(stock_symbol=form.stock_symbol.data, 
                          quantity=form.quantity.data, price=form.price.data, 
                          stockholder=current_user)
        db.session.add(stock)
        db.session.commit()
        flash('Your stock has been added to Portfolio!', 'success')
        return redirect(url_for('home'))
    return render_template('portfolio.html', title='Portfolio', form=form)


@app.route('/test/register', methods = ["POST"])
def test_dummy_login():
    try:
        # get payload values sent from FE
        email = request.json['email']
        username = request.json['username']
        password = request.json['password']
        confirm_password = request.json['confirm_password'] 
        
        # verify if username is taken or not
        does_username_exist = User.query.filter_by(username=username).first()
        if does_username_exist:
            return { 'Error': 'Username already exists' }
        
        # verify if email is taken or not
        does_email_exist = User.query.filter_by(email=email).first()
        if does_email_exist:
            return { 'Error': 'Email already exists' }

        # verify if pass eq to confirm pass
        if password != confirm_password:
            return { 'Error': 'Passwords donot match' }
    
        # hash pass before saving to db
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return { 'Success': 'Your account has been created!' }
    except Exception as e:
        print(e)
        return { 'Error': 'Something went wrong!' }

@app.route('/<stock_name>')
@login_required
def get_stock_info(stock_name):
    ticker = yf.Ticker(stock_name)

    # Extract relevant information from the ticker
    ticker_info = ticker.info
    actions_df = json.loads(ticker.get_actions().to_json())
    div_df = json.loads(ticker.get_dividends().to_json())
    split_df = json.loads(ticker.get_splits().to_json())
    cap_gain_df = json.loads(ticker.get_capital_gains().to_json())

    # Return the response as JSON
    return { 'info':ticker_info,
            'actions':actions_df, 
            'dividend': div_df, 
            'split': split_df,
            'capital_gains':cap_gain_df}
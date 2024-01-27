from flask import render_template, request, flash, url_for, redirect, flash
from stock import app, db, bcrypt
from stock.forms import RegistrationForm, LoginForm
from stock.models import User, Portfolio
import email_validator
import yfinance as yf
import json
  
stocks = [
    {
        'Name':'IRFC',
        'Analysts':'Good Buy',
        'Hold':'One Year',
        'Target':'250'
    },
    {
        'Name':'IREDA',
        'Analysts':'Strong Buy',
        'Hold':'2 years',
        'Target':'350'
    }
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', stocks=stocks)

@app.route('/register', methods = ['GET', 'POST'])
def register():
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
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'dev@demo.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check in username and password.', 'danger')
    return render_template('login.html', title = 'login', form=form)

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
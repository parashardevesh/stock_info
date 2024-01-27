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

@app.route('/test/login', methods = ["POST"])
def test_dummy_login():
    username = request.json['username']
    password = request.json['password']
    
    if username == 'devesh' and password == 'devesh':
        return { 'username': username, 'password':password }
    else:
        return { 'error': 'user not found' }

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
from flask import request
from stock import app, db, bcrypt
from flask_login import login_required
from stock.models import User
import yfinance as yf
import json

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
from flask import Flask, render_template, url_for, request
import yfinance as yf
import pandas as pd
import json
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)


app.config['SECRET_KEY'] = '01c59a8611d6bc670d64ae69b2a2df'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(50), nullable = False)
    portfolios = db.relationship('Portfolio', backref='stockholder', lazy=True) #Portfolio is in uppercase because i am referring to actual Portfolio class
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #user is in lowercase in ForeignKey because now I am referring to table and column name

    def __repr__(self):
        return f"Portfolio('{self.stock_symbol}','{self.quantity}','{self.price}','{self.date}')"
    
    
stock = [
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
def Welcome():
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST']  )
def register():
    form = RegistrationForm()
    return render_template('register.html', topic = 'Register', form=form)

@app.route('/login', methods = ['GET', 'POST'] )
def login():
    form = LoginForm()
    return render_template('login.html', topic = 'login', form=form)

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
    
if __name__ == '__main__':
    app.run(debug=True)
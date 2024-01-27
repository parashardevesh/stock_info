from datetime import datetime
from stock import db

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
    
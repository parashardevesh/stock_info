from flask import Blueprint, render_template, request
from stock.models import Portfolio

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    portfolios = Portfolio.query.order_by(Portfolio.date.desc()).paginate(page=page, per_page = 4)
    return render_template('home.html', portfolios=portfolios) 
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from stock import db
from stock.models import Portfolio
from stock.portfolios.forms import PortfolioForm

portfolios = Blueprint('portfolios', __name__)

@portfolios.route('/portfolio/new', methods = ['GET', 'POST'])
@login_required
def new_portfolio():
    form = PortfolioForm()
    if form.validate_on_submit():
        portfolio = Portfolio(stock_symbol=form.stock_symbol.data, 
                          quantity=form.quantity.data, price=form.price.data, 
                          stockholder=current_user)
        db.session.add(portfolio)
        db.session.commit()
        flash('Your stock has been added to Portfolio!', 'success')
        return redirect(url_for('main.home'))
    return render_template('portfolio_new.html', title='Portfolio', form=form)

@portfolios.route('/portfolio/<int:portfolio_id>')
def portfolio(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('portfolio.html', title=portfolio.stock_symbol, portfolio=portfolio)

@portfolios.route("/portfolio/<int:portfolio_id>/update", methods=['GET', 'POST'])
@login_required
def update_portfolio(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    if portfolio.stockholder != current_user:
        abort(403)
    form = PortfolioForm()
    if form.validate_on_submit():
        portfolio.stock_symbol = form.stock_symbol.data
        portfolio.quantity = form.quantity.data
        portfolio.price = form.price.data
        db.session.commit()
        flash('Your portfolio has been updated!', 'success')
        return redirect(url_for('portfolios.portfolio', portfolio_id=portfolio.id))
    elif request.method == 'GET':
        form.stock_symbol.data = portfolio.stock_symbol
        form.quantity.data = portfolio.quantity
        form.price.data = portfolio.price
    return render_template('portfolio_new.html', title='Update Portfolio',
                           form=form, legend='Update Portfolio')

@portfolios.route("/portfolio/<int:portfolio_id>/delete", methods=['POST'])
@login_required
def delete_portfolio(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    if portfolio.stockholder != current_user:
        abort(403)
    db.session.delete(portfolio)
    db.session.commit()
    flash('Your portfolio has been deleted!', 'success')
    return redirect(url_for('main.home'))

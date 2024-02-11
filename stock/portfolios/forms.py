from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField
from wtforms.validators import DataRequired, InputRequired, Length

class PortfolioForm(FlaskForm):
    stock_symbol = StringField('Stock', validators=[DataRequired(), Length(min=2, max=20)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), InputRequired()])
    price = DecimalField('Price Limit',validators=[DataRequired(), InputRequired()])
    submit = SubmitField('Add')            
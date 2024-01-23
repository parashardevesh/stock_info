from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import json

app = Flask(__name__)

@app.route('/')
def Welcome():
    return render_template('index.html')


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
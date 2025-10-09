import asyncio
import pandas as pd
import json
import datetime
import requests

from .order_execution import place_order

def make_market(df):
    # Example function to make market based on the processed data
    symbol = df['Symbol'].values[0]
    last_price = float(df['Last price'].values[0])
    best_bid = float(df['Best bid price'].values[0])
    best_ask = float(df['Best ask price'].values[0])
    
    # Define your market making strategy here
    spread = best_ask  - best_bid
    mid_price = (best_ask + best_bid) / 2
    
    # Example: Place buy order slightly below mid price and sell order slightly above mid price
    buy_price = mid_price - (spread * 0.1)
    sell_price = mid_price + (spread * 0.1)

    quantity = 0.00847000
    
    # Print the intended orders (replace with actual API calls to place orders)
    print(f"Placing Buy Order: {symbol} at {buy_price}")
    asyncio.create_task(place_order(symbol, 'BUY', buy_price, quantity, order_type='LIMIT', timeInForce="GTC"))
    # place_order(symbol, 'BUY', buy_price, quantity, order_type='LIMIT')


    print(f"Placing Sell Order: {symbol} at {sell_price}")
    
    # Here you would add the code to place orders using Binance API
    # For example:
    # place_order(symbol, 'BUY', buy_price, quantity)
    # place_order(symbol, 'SELL', sell_price, quantity)


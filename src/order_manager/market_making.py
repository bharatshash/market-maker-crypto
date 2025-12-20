import asyncio
import pandas as pd
import json
import datetime
import requests

from .order_execution import place_order
from .order_execution import cancel_order
from .account_info import get_account_info
from .account_info import allocation
from .account_info import has_buy_position
from .account_info import has_active_buy_orders
from .account_info import has_sell_position
from .account_info import has_active_sell_orders
# from .risk_management.risk_calculation import kill_switch

# Configuration parameters
BUY_OFFSET = 0.01  # Offset to subtract from best_bid for buy orders (in price units)
DEFAULT_QUANTITY = 0.00847000  # Default quantity for orders

async def make_market(df):
    

    # Establish Websocket API connection for all requests

    # If kill switch is activated, do not make market and then cancel all orders

    # if(kill_switch(df)):
    #     print("Kill switch activated. Cancelling all orders.")
    #     # Here you would add the code to cancel all open orders using Binance API

    #     return

    # Extract market data from the processed data
    symbol = df['Symbol'].values[0]
    last_price = float(df['Last price'].values[0])
    best_bid = float(df['Best bid price'].values[0])
    best_ask = float(df['Best ask price'].values[0])

    # Check if there are active buy orders and buy positions
    try:
        # has_buy_orders = asyncio.create_task(has_active_buy_orders(symbol))
        # has_buy_pos = asyncio.create_task(has_buy_position(symbol))

        has_buy_orders = await has_active_buy_orders(symbol)
        has_buy_pos = await has_buy_position(symbol)

        # If no active buy order and no active position on buy side
        if not has_buy_orders and not has_buy_pos:
            # Compute buy price: bid_price = best_bid - buy_offset
            bid_price = best_bid - BUY_OFFSET
            
            print(f"No active buy order and no buy position detected for {symbol}")
            print(f"Placing buy order at {bid_price} (best_bid: {best_bid}, offset: {BUY_OFFSET})")
            
            # Place limit buy order
            await place_order(
                symbol=symbol, 
                side='BUY', 
                price=bid_price, 
                quantity=DEFAULT_QUANTITY, 
                order_type='LIMIT', 
                timeInForce='GTC'
            )
        else:
            if has_buy_orders:
                print(f"Active buy orders exist for {symbol}, skipping buy order placement")
                # Check for market proximity to existing buy orders here (not implemented)
            if has_buy_pos:
                print(f"Active buy position exists for {symbol}, skipping buy order placement")
                
    except Exception as e:
        print(f"Error checking orders/positions or placing buy order: {e}")

    # Here add code to check for active sell order and position and place limit order

    try:
        has_sell_orders = await has_active_sell_orders(symbol)  # Placeholder for sell order check
        has_sell_pos = await has_sell_position(symbol)  # Placeholder for sell position check

        # If no active sell order and no active position on sell side
        if not has_sell_orders and not has_sell_pos:
            # Compute sell price: ask_price = best_ask + sell_offset
            ask_price = best_ask + BUY_OFFSET  # Using BUY_OFFSET as placeholder
            
            print(f"No active sell order and no sell position detected for {symbol}")
            print(f"Placing sell order at {ask_price} (best_ask: {best_ask}, offset: {BUY_OFFSET})")
            
            # Place limit sell order
            await place_order(
                symbol=symbol, 
                side='SELL', 
                price=ask_price, 
                quantity=DEFAULT_QUANTITY, 
                order_type='LIMIT', 
                timeInForce='GTC'
            )
        else:
            if has_sell_orders:
                print(f"Active sell orders exist for {symbol}, skipping sell order placement")
                # Check for market proximity to existing sell orders here (not implemented)
            if has_sell_pos:
                print(f"Active sell position exists for {symbol}, skipping sell order placement")

    except Exception as e:
        print(f"Error checking orders/positions or placing sell order: {e}")

    # If active order exists check whther market came within proximity  
        
    
    # Define your market making strategy here
    spread = best_ask  - best_bid
    mid_price = (best_ask + best_bid) / 2
    
    # Example: Place buy order slightly below mid price and sell order slightly above mid price
    buy_price = mid_price - (spread * 0.1)
    sell_price = mid_price + (spread * 0.1)

    quantity = 0.00847000
    
    # Print the intended orders (replace with actual API calls to place orders)
    # print(f"Placing Buy Order: {symbol} at {buy_price}")
    # # asyncio.create_task(place_order(symbol, 'BUY', buy_price, quantity, order_type='LIMIT', timeInForce="GTC"))

    # orderId = 'nRS6OvQsX93tUsM0B0UMcz'
    # print(f"Cancelling Buy Order: {symbol} for {orderId}")
    # # place_order(symbol, 'BUY', buy_price, quantity, order_type='LIMIT')
    # # asyncio.create_task(cancel_order(symbol, orderId))


    # print(f"Placing Sell Order: {symbol} at {sell_price}")

    # asyncio.create_task(get_account_info())
    # asyncio.create_task(allocation(symbol))
    
    # Here you would add the code to place orders using Binance API
    # For example:
    # place_order(symbol, 'BUY', buy_price, quantity)
    # place_order(symbol, 'SELL', sell_price, quantity)

    # await get_account_info()


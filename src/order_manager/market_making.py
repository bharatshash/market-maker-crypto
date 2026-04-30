"""
    This module is used to implement market making strategy.
    It is used to place buy and sell orders in the market.

    run_buy_side function is used to place buy orders in the market.

    run_sell_side function is used to place sell orders in the market.

    make_market function is used to make market in the market.

    the make_market function is the main function that is called by the 
    process_data module. It also implements a kill switch to stop 
    the market making process if the kill switch is activated.
 
"""


import asyncio
import pandas as pd
import json
import datetime
import requests
import concurrent.futures
import threading

from .order_execution import cancel_open_orders, place_order
from .order_execution import cancel_order
from .account_info import get_account_info
from .account_info import allocation
from .account_info import has_buy_position
from .account_info import has_active_buy_orders
from .account_info import has_sell_position
from .account_info import has_active_sell_orders
from risk_manager.kill_switch import kill_switch

# Configuration parameters
BUY_OFFSET = 1000  # Offset to subtract from best_bid for buy orders (in price units)
DEFAULT_QUANTITY = 0.00847000  # Default quantity for orders


async def run_buy_side(symbol, best_bid):
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
                print(f"Active buy orders exist for {symbol}, skipping order")
                # Check for market proximity to existing buy orders here (not implemented)
                
            if has_buy_pos:
                print(f"Active buy position exists for {symbol}, skipping order")
                
    except Exception as e:
        print(f"Error checking orders/positions or placing buy order: {e}")

async def run_sell_side(symbol, best_ask):
     # Here add code to check for active sell order and position and place limit order

    try:
        has_sell_orders = await has_active_sell_orders(symbol) 
        has_sell_pos = await has_sell_position(symbol)

        # If no active sell order and no active position on sell side
        if not has_sell_orders and not has_sell_pos:
            # Compute sell price: ask_price = best_ask + sell_offset
            ask_price = best_ask + BUY_OFFSET  # Using BUY_OFFSET as placeholder
            
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
                print(f"Active sell orders exist for {symbol}, skipping order")
                # Check for market proximity to existing sell orders here (not implemented)
            if has_sell_pos:
                print(f"Active sell position exists for {symbol}, skipping order")

    except Exception as e:
        print(f"Error checking orders/positions or placing sell order: {e}")

async def make_market(df):
    

    # Extract market data from the processed data
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

    # If kill switch is activated, do not make market and then cancel all orders
    
    kill_switch.check_kill(float(mid_price))

    if(kill_switch.is_active()):
        print("Kill switch activated. Cancelling all orders.")
        cancel_open_orders(symbol)
        return

    await asyncio.gather(
        run_buy_side(symbol, best_bid),
        run_sell_side(symbol, best_ask)
    )
 


    # orderId = 'nRS6OvQsX93tUsM0B0UMcz'
    # print(f"Cancelling Buy Order: {symbol} for {orderId}")
    # # place_order(symbol, 'BUY', buy_price, quantity, order_type='LIMIT')
    # # asyncio.create_task(cancel_order(symbol, orderId))


    # asyncio.create_task(get_account_info())
    # asyncio.create_task(allocation(symbol))
    
    # await get_account_info()


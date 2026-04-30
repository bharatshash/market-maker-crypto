"""
    This module is used to execute different types of functions related to your orders in the market.

    It includes the following functions:
    
    place_order: Used to place an order in the market.

    cancel_order: Used to cancel an order in the market.

    cancel_open_orders: Used to cancel all open orders in the market.

    The "websocket_manager" class is used to manage the WebSocket connection to the exchange.



"""

import asyncio
import os
import logging

from binance_sdk_spot.websocket_api.models import AccountCommissionResponse
from binance_sdk_spot.websocket_api.models import OrderPlaceSideEnum
from binance_sdk_spot.websocket_api.models import OrderPlaceTypeEnum
from binance_sdk_spot.websocket_api.models import OrderPlaceTimeInForceEnum
from .websocket_manager import ws_manager
# from market_data.process_data import process_exchangeinfo

logging.basicConfig(level=logging.INFO)


async def place_order(symbol, side, price, quantity, order_type = OrderPlaceTypeEnum["LIMIT"].value, timeInForce = OrderPlaceTimeInForceEnum["GTC"].value):
    """Place an order in the market"""
    
    async def _place_order_operation(connection, symbol, side, price, quantity, order_type, timeInForce):
        response = await connection.order_place(
            symbol=symbol,
            side=OrderPlaceSideEnum[side].value,
            type=order_type,
            quantity=quantity,
            price=round(price, 2),
            time_in_force=timeInForce,
        )

        # Check if response has data before accessing it
        if hasattr(response, 'data') and callable(response.data):
            try:
                data = response.data()
                # logging.info(f"order_place() response: {data}")
                return data
            except Exception as e:
                logging.error(f"Data Error: {e}")
                return None
        else:
            logging.error("Data might not exist")
            return None

    try:
        return await ws_manager.execute_with_retry(
            _place_order_operation, 
            symbol, side, price, quantity, order_type, timeInForce
        )
    except Exception as e:
        logging.error(f"Error placing order: {e}")
        raise


async def cancel_order(symbol, orig_client_order_id):
    """Cancel an order in the market"""
    async def _cancel_order_operation(connection, symbol, orig_client_order_id):
        response = await connection.order_cancel(
            symbol=symbol,
            orig_client_order_id=orig_client_order_id
        )

        # Check if response has data before accessing it
        if hasattr(response, 'data') and callable(response.data):
            try:
                data = response.data()
                logging.info(f"order_cancel() response: {data}")
                return data
            except Exception as e:
                logging.error(f"Error getting data response: {e}")
                return None
        else:
            logging.error("Order cancel response does not have data value")
            return None

    try:
        return await ws_manager.execute_with_retry(
            _cancel_order_operation, 
            symbol, orig_client_order_id
        )
    except Exception as e:
        logging.error(f"cancel_order() error: {e}")
        raise

async def cancel_open_orders(symbol):
    """Cancel all open orders for a symbol"""
    async def _cancel_open_orders_operation(connection, symbol):
        response = await connection.open_orders_cancel_all(
            symbol=symbol
        )

        data = response.data()
        logging.info(f"open_orders_cancel_all() response: {data}")
        return data

    try:
        return await ws_manager.execute_with_retry(
            _cancel_open_orders_operation, 
            symbol
        )
    except Exception as e:
        logging.error(f"cancel_open_orders() error: {e}")
        raise
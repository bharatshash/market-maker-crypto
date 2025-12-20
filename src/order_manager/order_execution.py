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

# async def get_exchange_info(connection):
#     exchange_resp = await connection.exchange_info()
#     process_exchangeinfo(exchange_resp.model_dump_json())



async def place_order(symbol, side, price, quantity, order_type = OrderPlaceTypeEnum["LIMIT"].value, timeInForce = OrderPlaceTimeInForceEnum["GTC"].value):
    """
    Place an order using the shared WebSocket connection
    """
    async def _place_order_operation(connection, symbol, side, price, quantity, order_type, timeInForce):
        response = await connection.order_place(
            symbol=symbol,
            side=OrderPlaceSideEnum[side].value,
            type=order_type,
            quantity=quantity,
            price=round(price, 2),
            time_in_force=timeInForce,
        )

        # Check rate limits first
        if hasattr(response, 'rate_limits'):
            rate_limits = response.rate_limits
            # logging.info(f"order_place() rate limits: {rate_limits}")

        # Check if response has data before accessing it
        if hasattr(response, 'data') and callable(response.data):
            try:
                data = response.data()
                # logging.info(f"order_place() response: {data}")
                return data
            except Exception as e:
                logging.error(f"Error getting data from order_place response: {e}")
                return None
        else:
            logging.error("Order place response does not have data method or result is not set")
            return None

    try:
        return await ws_manager.execute_with_retry(
            _place_order_operation, 
            symbol, side, price, quantity, order_type, timeInForce
        )
    except Exception as e:
        logging.error(f"Error placing orderr: {e}")
        raise

# async def handle_fill():


async def cancel_order(symbol, orig_client_order_id):
    """
    Cancel an order using the shared WebSocket connection
    """
    async def _cancel_order_operation(connection, symbol, orig_client_order_id):
        response = await connection.order_cancel(
            symbol=symbol,
            orig_client_order_id=orig_client_order_id
        )

        # Check rate limits first
        if hasattr(response, 'rate_limits'):
            rate_limits = response.rate_limits
            # logging.info(f"order_cancel() rate limits: {rate_limits}")

        # Check if response has data before accessing it
        if hasattr(response, 'data') and callable(response.data):
            try:
                data = response.data()
                logging.info(f"order_cancel() response: {data}")
                return data
            except Exception as e:
                logging.error(f"Error getting data from order_cancel response: {e}")
                return None
        else:
            logging.error("Order cancel response does not have data method or result is not set")
            return None

    try:
        return await ws_manager.execute_with_retry(
            _cancel_order_operation, 
            symbol, orig_client_order_id
        )
    except Exception as e:
        logging.error(f"cancel_order() error: {e}")
        raise

async def get_open_orders(symbol):
    """
    Get all open orders for a symbol using the shared WebSocket connection
    """
    async def _get_open_orders_operation(connection, symbol):
        response = await connection.open_orders_status(
            symbol=symbol
        )

        # Check rate limits first
        if hasattr(response, 'rate_limits'):
            rate_limits = response.rate_limits
            logging.info(f"open_orders_status() rate limits: {rate_limits}")

        # Check if response has data before accessing it
        if hasattr(response, 'data') and callable(response.data):
            try:
                data = response.data()
                logging.info(f"open_orders_status() response type: {type(data)}")
                logging.info(f"open_orders_status() response: {data}")
                return data
            except Exception as e:
                logging.error(f"Error getting data from open_orders response: {e}")
                return []
        else:
            logging.error("Open orders response does not have data method or result is not set")
            return []

    try:
        return await ws_manager.execute_with_retry(
            _get_open_orders_operation, 
            symbol
        )
    except Exception as e:
        logging.error(f"get_open_orders() error: {e}")
        return []

async def has_active_buy_orders(symbol):
    """Check if there are any active BUY orders for the given symbol"""
    open_orders = await get_open_orders(symbol)
    
    # Handle different response types
    if open_orders is None:
        return False
    
    # If it's a list, check length directly
    if isinstance(open_orders, list):
        if len(open_orders) == 0:
            return False
        orders_to_check = open_orders
    # If it's a dict, look for orders in common keys
    elif isinstance(open_orders, dict):
        # Try common keys where orders might be stored
        orders_to_check = open_orders.get('orders', open_orders.get('data', []))
        if not isinstance(orders_to_check, list):
            orders_to_check = []
        if len(orders_to_check) == 0:
            return False
    else:
        # If it's neither list nor dict, try to get length if possible
        try:
            if hasattr(open_orders, '__len__') and len(open_orders) == 0:
                return False
            # If it's an object with an orders attribute
            if hasattr(open_orders, 'orders'):
                orders_to_check = open_orders.orders
            else:
                # Log the type for debugging
                logging.warning(f"Unexpected open_orders type: {type(open_orders)}")
                return False
        except TypeError:
            logging.error(f"Cannot check length of open_orders type: {type(open_orders)}")
            return False
    
    # Check if any of the open orders are BUY orders
    for order in orders_to_check:
        if isinstance(order, dict) and order.get('side') == 'BUY':
            return True
    
    return False

async def cancel_open_orders(symbol):
    """
    Cancel all open orders for a symbol using the shared WebSocket connection
    """
    async def _cancel_open_orders_operation(connection, symbol):
        response = await connection.open_orders_cancel_all(
            symbol=symbol
        )

        rate_limits = response.rate_limits
        logging.info(f"open_orders_cancel_all() rate limits: {rate_limits}")

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
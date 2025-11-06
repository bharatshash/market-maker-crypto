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

        rate_limits = response.rate_limits
        logging.info(f"order_place() rate limits: {rate_limits}")

        data = response.data()
        logging.info(f"order_place() response: {data}")
        return data

    try:
        return await ws_manager.execute_with_retry(
            _place_order_operation, 
            symbol, side, price, quantity, order_type, timeInForce
        )
    except Exception as e:
        logging.error(f"place_order() error: {e}")
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

        rate_limits = response.rate_limits
        logging.info(f"order_cancel() rate limits: {rate_limits}")

        data = response.data()
        logging.info(f"order_cancel() response: {data}")
        return data

    try:
        return await ws_manager.execute_with_retry(
            _cancel_order_operation, 
            symbol, orig_client_order_id
        )
    except Exception as e:
        logging.error(f"cancel_order() error: {e}")
        raise

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
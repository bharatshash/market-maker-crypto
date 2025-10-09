import asyncio
import os
import logging

from binance_common.configuration import ConfigurationWebSocketAPI
from binance_common.constants import SPOT_WS_API_TESTNET_URL
from binance_sdk_spot.spot import Spot
from binance_sdk_spot.websocket_api.models import AccountCommissionResponse
from binance_sdk_spot.websocket_api.models import OrderPlaceSideEnum
from binance_sdk_spot.websocket_api.models import OrderPlaceTypeEnum
from binance_sdk_spot.websocket_api.models import OrderPlaceTimeInForceEnum
# from market_data.process_data import process_exchangeinfo

binance_api_url = 'wss://ws-api.testnet.binance.vision/ws-api/v3'
binance_api_key = 'CSziIqAFEyb2CCTj8MVdzRkKESBXJqXGOo3y4zLI1wbNsgHIA3W4QrJqKLgUxYRZ'
binance_api_secret = 'uY21UyeY5ppc8xawA695BYdjNUf69I0ES23P8UwELxW9bsfTXQfXKIa3AhhwJpVY'

logging.basicConfig(level=logging.INFO)

configuration_ws_api = ConfigurationWebSocketAPI(
    api_key = os.getenv("API_KEY", binance_api_key),
    api_secret = os.getenv("API_SECRET", binance_api_secret),
    stream_url = os.getenv("STREAM_URL", SPOT_WS_API_TESTNET_URL)
)

# Initiailize client for WebSocket API
client_ws_api = Spot(config_ws_api=configuration_ws_api)

# async def get_exchange_info(connection):
#     exchange_resp = await connection.exchange_info()
#     process_exchangeinfo(exchange_resp.model_dump_json())



async def place_order(symbol, side, price, quantity, order_type = OrderPlaceTypeEnum["LIMIT"].value, timeInForce = OrderPlaceTimeInForceEnum["GTC"].value):
    connection = None
    try:
        connection = await client_ws_api.websocket_api.create_connection()

        # await exchange_resp = await connection.exchange_info(symbol=symbol)

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


    except Exception as e:
        logging.error(f"place_order() connection error: {e}")
    finally:
        if connection:
            await connection.close_connection(close_session=True)




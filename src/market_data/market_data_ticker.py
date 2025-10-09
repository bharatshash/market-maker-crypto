import asyncio
import os
import logging



from binance_sdk_spot.spot import (
    Spot,
    SPOT_WS_STREAMS_PROD_URL,
    ConfigurationWebSocketStreams,
)

from .process_data import process_market_data as process


# Configure logging
logging.basicConfig(level=logging.INFO)

# Create configuration for the WebSocket Streams
configuration_ws_streams = ConfigurationWebSocketStreams(
    stream_url=os.getenv("STREAM_URL", SPOT_WS_STREAMS_PROD_URL)
)

# Testnet Configuration for Websocketstream
configuration_ws_streams_testnet = ConfigurationWebSocketStreams(
    stream_url=os.getenv("STREAM_URL", "wss://stream.testnet.binance.vision:9443")
)

# Initialize Spot client
client = Spot(config_ws_streams=configuration_ws_streams)


def on_message(data):
    # process_data(data.model_dump_json())
    try:
        process(data.model_dump_json())  # use model_dump_json() if you want JSON
    except Exception as e:
        logging.error(f"process_data error: {e}")

async def ticker():
    connection = None
    try:
        connection = await client.websocket_streams.create_connection()

        stream = await connection.ticker(
            symbol="btcusdt",
        )
        stream.on("message",on_message)

        await asyncio.sleep(5)
        await stream.unsubscribe()
    except Exception as e:
        logging.error(f"ticker() error: {e}")
    finally:
        if connection:
            await connection.close_connection(close_session=True)

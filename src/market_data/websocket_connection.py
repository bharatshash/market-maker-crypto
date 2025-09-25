import asyncio
import os
import logging
import zmq
import time

from binance_sdk_spot.spot import (
    Spot,
    SPOT_WS_STREAMS_PROD_URL,
    ConfigurationWebSocketStreams,
)


# Configure logging
logging.basicConfig(level=logging.INFO)

# Create configuration for the WebSocket Streams
configuration_ws_streams = ConfigurationWebSocketStreams(
    stream_url=os.getenv("STREAM_URL", SPOT_WS_STREAMS_PROD_URL)
)

# Initialize Spot client
client = Spot(config_ws_streams=configuration_ws_streams)

# Initialize server for websocket connection with cpp client
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

# while True:
#     #  Wait for next request from client
#     message = socket.recv()
#     print("Received request: %s" % message)

#     #  Do some 'work'   
#     time.sleep(1)

#     #  Send reply back to client
#     socket.send(b"World")




async def ticker():
    connection = None
    try:
        connection = await client.websocket_streams.create_connection()

        stream = await connection.ticker(
            symbol="bnbusdt",
        )

        def on_message(data):
            print(f"Message: {data}")
            message = socket.recv()
            print("Client Request: %s" % message)

            socket.send_json(data)

        stream.on("message", on_message)

        await asyncio.sleep(30)
        await stream.unsubscribe()
    except Exception as e:
        logging.error(f"ticker() error: {e}")
    finally:
        if connection:
            await connection.close_connection(close_session=True)


if __name__ == "__main__":
    asyncio.run(ticker())
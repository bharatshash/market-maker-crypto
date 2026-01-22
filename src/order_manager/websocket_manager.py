import asyncio
import os
import logging
from typing import Optional

from binance_common.configuration import ConfigurationWebSocketAPI
from binance_common.constants import SPOT_WS_API_TESTNET_URL
from binance_sdk_spot.spot import Spot

# Define the Binance API endpoint and related Keys
binance_api_url = 'https://api.binance.com/api/v3/'
binance_api_key = 'CSziIqAFEyb2CCTj8MVdzRkKESBXJqXGOo3y4zLI1wbNsgHIA3W4QrJqKLgUxYRZ'
binance_api_secret = 'uY21UyeY5ppc8xawA695BYdjNUf69I0ES23P8UwELxW9bsfTXQfXKIa3AhhwJpVY'

class WebSocketConnectionManager:
    """
    Class to manage WebSocket connection in the application
    """
    
    _instance = None
    _connection = None
    _client = None
    _is_connected = False
    _connection_lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebSocketConnectionManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.binance_api_key = binance_api_key
            self.binance_api_secret = binance_api_secret
            
            # Create configuration for the WebSocket API
            self.configuration_ws_api = ConfigurationWebSocketAPI(
                api_key=os.getenv("API_KEY", self.binance_api_key),
                api_secret=os.getenv("API_SECRET", self.binance_api_secret),
                stream_url=os.getenv("STREAM_URL", SPOT_WS_API_TESTNET_URL),
            )
            
            # Initialize Spot client
            self._client = Spot(config_ws_api=self.configuration_ws_api)
            self.initialized = True
            
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
    
    async def get_connection(self):
        """
        Get the current WebSocket connection, creating one if it doesn't exist
        """
        async with self._connection_lock:
            if not self._is_connected or self._connection is None:
                await self._create_connection()
            return self._connection
    
    async def _create_connection(self):
        """
        Create a new WebSocket connection
        """
        try:
            if self._connection:
                await self._close_connection_internal()
            
            self.logger.info("Creating new WebSocket connection...")
            self._connection = await self._client.websocket_api.create_connection()
            self._is_connected = True
            self.logger.info("WebSocket connection established successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create WebSocket connection: {e}")
            self._is_connected = False
            self._connection = None
            raise
    
    async def _close_connection_internal(self):
        """
        Internal method to close the connection without acquiring the lock
        """
        if self._connection:
            try:
                await self._connection.close_connection(close_session=True)
                self.logger.info("WebSocket connection closed")
            except Exception as e:
                self.logger.error(f"Error closing WebSocket connection: {e}")
            finally:
                self._connection = None
                self._is_connected = False
    
    async def close_connection(self):
        """
        Close the WebSocket connection
        """
        async with self._connection_lock:
            await self._close_connection_internal()
    
    async def reconnect(self):
        """
        Force reconnection by closing current connection and creating a new one
        """
        async with self._connection_lock:
            self.logger.info("Forcing WebSocket reconnection...")
            await self._close_connection_internal()
            await self._create_connection()
    
    async def execute_with_retry(self, operation, *args, **kwargs):
        """
        Execute an operation with automatic retry on connection failure
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                connection = await self.get_connection()
                return await operation(connection, *args, **kwargs)
                
            except Exception as e:
                self.logger.error(f"Operation failed on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    
                    # Try to reconnect for the next attempt
                    try:
                        await self.reconnect()
                    except Exception as reconnect_error:
                        self.logger.error(f"Reconnection failed: {reconnect_error}")
                    
                    retry_delay *= 2  # Exponential backoff
                else:
                    self.logger.error(f"Operation failed after {max_retries} attempts")
                    raise
    
    def is_connected(self):
        """
        Check if the WebSocket connection is currently active
        """
        return self._is_connected and self._connection is not None

# Global instance
ws_manager = WebSocketConnectionManager()
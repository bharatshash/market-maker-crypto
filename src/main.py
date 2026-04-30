import asyncio
import signal
import logging
from market_data import ticker
from market_data import process_data as process
from order_manager.websocket_manager import ws_manager
from risk_manager.kill_switch import kill_switch

# Configure console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):

    global shutdown_flag
    logger.info(f"Initiating shutdown...")
    shutdown_flag = True

async def main():
    """Main application entry point"""
    global shutdown_flag
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Starting Market Maker:")
        
        # Initialize the WebSocket connection manager
        logger.info("Initializing WebSocket connection...")
        await ws_manager.get_connection()
        logger.info("WebSocket connection initialized successfully")
        
        # Start the ticker data stream
        logger.info("Starting market data ticker...")
        ticker_task = asyncio.create_task(ticker())
        
        # Wait for shutdown signal or ticker completion
        while not shutdown_flag:
            if ticker_task.done():
                # If ticker task is done, check if it had an exception
                try:
                    await ticker_task
                except Exception as e:
                    logger.error(f"Ticker task failed: {e}")
                break
            
            await asyncio.sleep(0.1)
        
        logger.info("Shutting down...")
        
        # Cancel ticker task if it's still running
        if not ticker_task.done():
            ticker_task.cancel()
            try:
                await ticker_task
            except asyncio.CancelledError:
                logger.info("Ticker task cancelled")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        # Clean up WebSocket connection
        logger.info("Closing WebSocket connection...")
        await ws_manager.close_connection()
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
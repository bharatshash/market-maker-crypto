import asyncio
from market_data import ticker
from market_data import process_data as process
# from market_data import process_exchangeinfo


# Define the Binance API endpoint and related Keys
binance_api_url = 'https://api.binance.com/api/v3/'
binance_api_key = 'YOUR_API_KEY'
binance_api_secret = 'YOUR_API_SECRET'

if __name__ == "__main__":
    asyncio.run(ticker())
    # await ticker()  # Call the ticker function
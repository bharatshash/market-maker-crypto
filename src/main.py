import asyncio
from market_data import ticker
from market_data import process_data as process

if __name__ == "__main__":
    asyncio.run(ticker())
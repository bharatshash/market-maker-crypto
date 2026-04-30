"""
    This module is used to process each tick into manageable logical dataframe for 
    proper implementation of relevant strategy.
    
"""

import pandas as pd
import json
import datetime
import asyncio
from typing import Set
from order_manager.market_making import make_market

# Keep a strong reference to background tasks
background_tasks: Set[asyncio.Task] = set()

def process_market_data(data: str) -> None:
    # print(type(data))
    data_dict = json.loads(data)
    df = pd.DataFrame([data_dict])
    df.rename(columns={
        'e': 'Event type',
        'E': 'Event time',
        's': 'Symbol',
        'p': 'Price change',
        'P': 'Price change percent',
        'w': 'Weighted average price',
        'x': 'First trade(F)-1 price',
        'c': 'Last price',
        'Q': 'Last quantity',
        'b': 'Best bid price',
        'B': 'Best bid quantity',
        'a': 'Best ask price',
        'A': 'Best ask quantity',
        'o': 'Open price',
        'h': 'High price',
        'l': 'Low price',
        'v': 'Total traded base asset volume',
        'q': 'Total traded quote asset volume',
        'O': 'Statistics open time',
        'C': 'Statistics close time',
        'F': 'First trade ID',
        'L': 'Last trade Id',
        'n': 'Total number of trades'
    }, inplace=True)
    
    # Since make_market is now async, we need to schedule it to run and keep a strong reference
    task = asyncio.create_task(make_market(df))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    

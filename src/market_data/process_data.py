"""
    This module is used to process each tick into manageable logical dataframe for 
    proper implementation of relevant strategy.
    
"""

import pandas as pd
import json
import datetime
import asyncio
from typing import Set, Dict, Any
from order_manager.market_making import make_market

# Keep a strong reference to background tasks
background_tasks: Set[asyncio.Task] = set()

# def process_market_data(data: str) -> None:
#     # print(type(data))
#     data_dict = json.loads(data)
#     df = pd.DataFrame([data_dict])
#     df.rename(columns={
#         'e': 'Event type',
#         'E': 'Event time',
#         's': 'Symbol',
#         'p': 'Price change',
#         'P': 'Price change percent',
#         'w': 'Weighted average price',
#         'x': 'First trade(F)-1 price',
#         'c': 'Last price',
#         'Q': 'Last quantity',
#         'b': 'Best bid price',
#         'B': 'Best bid quantity',
#         'a': 'Best ask price',
#         'A': 'Best ask quantity',
#         'o': 'Open price',
#         'h': 'High price',
#         'l': 'Low price',
#         'v': 'Total traded base asset volume',
#         'q': 'Total traded quote asset volume',
#         'O': 'Statistics open time',
#         'C': 'Statistics close time',
#         'F': 'First trade ID',
#         'L': 'Last trade Id',
#         'n': 'Total number of trades'
#     }, inplace=True)
    
#     # Since make_market is now async, we need to schedule it to run and keep a strong reference
#     task = asyncio.create_task(make_market(df))
#     background_tasks.add(task)
#     task.add_done_callback(background_tasks.discard)
    
def process_market_data(data:str) -> None:

    try:
        data_dict : Dict[str,Any] = json.loads(data)

        parsed_data = {
            'Event type': data_dict.get('e'),
            'Event time': data_dict.get('E'),
            'Symbol': data_dict.get('s'),
            'Price change': data_dict.get('p'),
            'Price change percent': data_dict.get('P'),
            'Weighted average price': data_dict.get('w'),
            'First trade(F)-1 price': data_dict.get('x'),
            'Last price': data_dict.get('c'),
            'Last quantity': data_dict.get('Q'),
            'Best bid price': data_dict.get('b'),
            'Best bid quantity': data_dict.get('B'),
            'Best ask price': data_dict.get('a'),
            'Best ask quantity': data_dict.get('A'),
            'Open price': data_dict.get('o'),
            'High price': data_dict.get('h'),
            'Low price': data_dict.get('l'),
            'Total traded base asset volume': data_dict.get('v'),
            'Total traded quote asset volume': data_dict.get('q'),
            'Statistics open time': data_dict.get('O'),
            'Statistics close time': data_dict.get('C'),
            'First trade ID': data_dict.get('F'),
            'Last trade Id': data_dict.get('L'),
            'Total number of trades': data_dict.get('n')
        }
        
        # Since make_market is now async, we need to schedule it to run and keep a strong reference
        task = asyncio.create_task(make_market(parsed_data))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        print(f"Error processing market data: {e}")

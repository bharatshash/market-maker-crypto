import pandas as pd
import json
import datetime
from order_manager.market_making import make_market

def process_data(data):
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
    print(df)
    make_market(df)

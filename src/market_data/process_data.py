import pandas as pd
import json
import datetime

def process_data(data):
    # print(type(data))
    data_dict = json.loads(data)
    df = pd.DataFrame([data_dict])
    print(df)

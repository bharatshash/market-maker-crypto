# Market Maker Crypto

A Market Making project to support algorithmic trading of Crypto Assets

> Binance Documentation used: https://developers.binance.com/docs/binance-spot-api-docs/
> Binance GitHub Link: https://github.com/binance/binance-connector-python/tree/master/clients/spot

## SETUP

Ensure you have the latest version of Python and pip then run the following commands to install the dependencies

> `pip install pandas`
> `pip install binance-sdk-spot`

## RUNNING CODE:

->From src run `py .\main.py'`

### CURRENT FEATURES/WORKFLOW

- Receives data stream from websocket

- With every ticker data is processed into data frame for market making

- Have a Websocket manager to maintain a single connection for all requests rather than repeated connect and disconnect for each reconnect

- Seperate Buy side and sell side logics (not a single function since has internal seperate buy and sell side function calls)

- Cancel order functions

- Active kill switch to cancel all open order on market fluctuation more than 5%

- Runs only for few seconds to allow proper testing and avoid depleting Binance testnet funds(Happened way too many times lol)

### FUTURE FEATURES/YET TO BE IMPLEMENTED

- Multithreading to run multiple symbols together, buy or sell side might not need it because of place order being async

- Trade execution based on proper strategy and pricing using plug and play modules

- Maintaining a local database/orderbook

- Have a proper config file when strategy is established (or when code is more prod ready)

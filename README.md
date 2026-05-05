# market-maker-crypto

> An asynchronous algorithmic market-making bot for Binance Spot, built in Python.

---

## Overview

`market-maker-crypto` implements a classic **symmetric market-making strategy** on the Binance Spot exchange.  
The bot continuously quotes a bid below the best bid and an ask above the best ask, capturing the spread while managing inventory risk through a price-movement kill switch.

Key design decisions:
- **Single persistent WebSocket connection** for all order-management API calls (no per-request connect/disconnect overhead).
- **Separate buy-side and sell-side coroutines** running concurrently via `asyncio.gather`.
- **FIFO realized PnL tracking** — only fully closed buy→sell round-trips are counted; open positions never inflate the figure.
- **Plug-and-play strategy layer** — `market_making.py` calls into a `strategy/` module so pricing logic can be swapped without touching order execution.

---

## Architecture

```
main.py
 ├── market_data/
 │    ├── market_data_ticker.py   # WebSocket stream → raw tick events
 │    └── process_data.py         # Parses tick JSON → dict, schedules make_market()
 │
 ├── order_manager/
 │    ├── websocket_manager.py    # Singleton WS connection with exponential-backoff retry
 │    ├── market_making.py        # Buy/sell side logic, kill-switch gate
 │    ├── order_execution.py      # place_order / cancel_order / cancel_open_orders
 │    └── account_info.py         # Balance queries, open-order checks, position checks
 │
 └── risk_manager/
      ├── kill_switch.py          # Price-movement circuit breaker (default: ±5 %)
      └── risk_calculation.py     # Realized & unrealized PnL from trade history
```

---

## Features

| Feature |
|---|
| Live ticker stream via Binance WebSocket Streams
| Persistent WebSocket API connection (singleton)
| Exponential-backoff reconnection (3 attempts)
| Limit buy / limit sell order placement
| Cancel single order / cancel all open orders
| Position & open-order guard (no duplicate orders)
| Price-movement kill switch (configurable %)
| FIFO realized PnL (commission-aware)
| Unrealized PnL from open inventory
| Graceful shutdown on SIGINT / SIGTERM
<!-- | Test-mode time limit (avoid draining testnet funds)
| Pluggable strategy module
| Local order book / database
| Dynamic spread / Avellaneda-Stoikov pricing -->

---

## Project Structure

```
market-maker-crypto/
├── src/
│   ├── main.py                        # Entry point
│   ├── config.py                      # All tunable parameters
│   ├── market_data/
│   │   ├── __init__.py
│   │   ├── market_data_ticker.py
│   │   └── process_data.py
│   ├── order_manager/
│   │   ├── __init__.py
│   │   ├── websocket_manager.py
│   │   ├── market_making.py
│   │   ├── order_execution.py
│   │   └── account_info.py
│   ├── risk_manager/
│   │   ├── kill_switch.py
│   │   └── risk_calculation.py
│   └── strategy/
│       └── long.py
├── tests/
│   └── test_pnl_tracker.py
├── .env                               # API credentials (never commit)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.10+
- A Binance account with API key/secret (testnet recommended for development)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/market-maker-crypto.git
cd market-maker-crypto

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install binance-sdk-spot pandas python-dotenv
```

### Environment Variables

Create a `.env` file in the project root (this file is git-ignored):

```env
API_KEY=your_binance_api_key
API_SECRET=your_binance_api_secret
STREAM_URL=wss://stream.testnet.binance.vision:9443   # omit for production
```

---

## Configuration

All tunable parameters live in `src/config.py`:

| Parameter | Default | Description |
|---|---|---|
| `TEST` | `True` | Enables test-mode (bot stops after `TICKER_TEST_RUN_TIME` seconds) |
| `TICKER_TEST_RUN_TIME` | `10` | Seconds to run before auto-shutdown in test mode |
| `KILL_SWITCH_THRESHOLD` | `5` | % price move that triggers the kill switch |
| `BUY_OFFSET` | `1000` | Amount subtracted from best bid for limit buy price (quote units) |
| `SELL_OFFSET` | `1000` | Amount added to best ask for limit sell price (quote units) |
| `DEFAULT_QUANTITY` | `0.00847` | Default order size in base asset (BTC) |
| `BASE_ASSET` | `"USDT"` | Quote asset used for balance checks |

> **Note:** `BUY_OFFSET` and `SELL_OFFSET` are intentionally large defaults to prevent fills during testing. Reduce them for live use.

---

## Running

```bash
# From the src/ directory
cd src
python main.py
```

The bot will:
1. Initialise the WebSocket API connection.
2. Subscribe to the `btcusdt` ticker stream.
3. On each tick, check for open orders / positions, then place a bid and an ask.
4. Monitor price movement and cancel all orders if the kill switch fires.
5. Shut down gracefully on `Ctrl+C` (SIGINT) or SIGTERM.

---

## Risk Management

### Kill Switch (`risk_manager/kill_switch.py`)

Compares the current mid-price against the previous tick. If the absolute percentage change exceeds `KILL_SWITCH_THRESHOLD`, `kill_switch.activate()` is called. The next `make_market()` invocation cancels all open orders and returns early.

```
price_change_pct = |current - previous| / previous × 100
if price_change_pct > KILL_SWITCH_THRESHOLD → activate
```

### Realized PnL (`risk_manager/risk_calculation.py`)

`get_realized_pnl(symbol)` fetches the full trade history and matches fills using **FIFO (First-In, First-Out)**:

1. Each buy fill is paired against the oldest unmatched sell (and vice versa).
2. Partial matches are supported — the residual stays in the open queue.
3. Any fill with no counter-part is placed in the open queue and **excluded from realized PnL**.
4. Commission is prorated by the matched fraction and deducted from both legs.

```
net_pnl = (sell_price − buy_price) × matched_qty − buy_commission − sell_commission
```

This guarantees that an isolated buy (or sell) with no closing leg contributes exactly **zero** to realized PnL.

---

## References

- [Binance Spot API Documentation](https://developers.binance.com/docs/binance-spot-api-docs/)
- [Binance Python SDK](https://github.com/binance/binance-connector-python/tree/master/clients/spot)
- [Avellaneda & Stoikov (2008) — High-frequency trading in a limit order book](https://www.math.nyu.edu/~avellane/HighFrequencyTrading.pdf)

from collections import deque
from order_manager.websocket_manager import ws_manager
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def get_unrealized_pnl(symbol: str, start_time: float = None, end_time: float = None) -> Optional[float]:
    """Get the unrealized PnL for a symbol"""

    async def _get_trade_history_operation(connection: any) -> Optional[float]:
        params = {
            "symbol": symbol,
            "startTime": int(start_time * 1000) if start_time else None,
            "endTime": int(end_time * 1000) if end_time else None
        }
        response = await connection.my_trades(**params)
    
    trades = await ws_manager.execute_with_retry(_get_trade_history_operation)        
    if trades is None or not hasattr(trades, 'result') or not hasattr(trades.result, 'trades'):
        return None
    
    unrealized_pnl = 0.0

    for trade in trades.result:
        qty = float(trade.qty)
        price = float(trade.price)
        commission = float(trade.commission)

        if trade.isBuyer:
            unrealized_pnl -= qty * price
        else:
            unrealized_pnl += qty * price
    
    return unrealized_pnl

async def get_realized_pnl(symbol: str) -> Optional[float]:
    """
    Get the realized PnL for a symbol using FIFO order matching.

    Only fully closed round-trips are counted:
      - Each buy fill is matched against the oldest unmatched sell, and vice versa.
      - Any leftover buy or sell fills with no counter-part are excluded entirely.
      - Commission is prorated and deducted on both the buy and sell leg of
        every matched pair.

    Returns None if the exchange call fails.
    """

    async def _get_trade_history_operation(connection: any) -> Optional[float]:
        params = {
            "symbol": symbol,
        }
        response = await connection.my_trades(**params)

    trades = await ws_manager.execute_with_retry(_get_trade_history_operation)
    if trades is None or not hasattr(trades, 'result') or not hasattr(trades.result, 'trades'):
        return None

    # ------------------------------------------------------------------ #
    # FIFO matching                                                        #
    # Each queue entry: [price, remaining_qty, remaining_commission]       #
    # ------------------------------------------------------------------ #
    open_buys  = deque()   # unmatched buy fills waiting for a sell
    open_sells = deque()   # unmatched sell fills waiting for a buy
    realized_pnl = 0.0

    for trade in trades.result:
        qty        = float(trade.qty)
        price      = float(trade.price)
        commission = float(trade.commission)

        # Mutable entry so we can reduce remaining qty/commission in-place
        incoming = [price, qty, commission]

        if trade.isBuyer:
            counter_queue = open_sells
            incoming_is_buy = True
        else:
            counter_queue = open_buys
            incoming_is_buy = False

        # Match incoming fill against the opposite queue (FIFO)
        while incoming[1] > 1e-12 and counter_queue:
            head = counter_queue[0]  # oldest unmatched counter-part

            matched_qty = min(incoming[1], head[1])

            # Prorate commission by the fraction of each fill being consumed
            incoming_comm = incoming[2] * (matched_qty / incoming[1])
            head_comm     = head[2]     * (matched_qty / head[1])

            buy_price  = incoming[0] if incoming_is_buy else head[0]
            sell_price = head[0]     if incoming_is_buy else incoming[0]

            gross = (sell_price - buy_price) * matched_qty
            net   = gross - incoming_comm - head_comm
            realized_pnl += net

            logger.debug(
                "Matched %.8f | buy @ %.4f sell @ %.4f | gross=%.6f comm=%.6f net=%.6f",
                matched_qty, buy_price, sell_price, gross,
                incoming_comm + head_comm, net,
            )

            # Reduce residuals
            incoming[1] -= matched_qty
            incoming[2] -= incoming_comm
            head[1]     -= matched_qty
            head[2]     -= head_comm

            if head[1] <= 1e-12:
                counter_queue.popleft()

        # Any un-matched residual goes into the open queue – NOT counted
        if incoming[1] > 1e-12:
            if incoming_is_buy:
                open_buys.append(incoming)
            else:
                open_sells.append(incoming)

    logger.info(
        "get_realized_pnl(%s): %.6f  |  open buys: %d fill(s)  open sells: %d fill(s)  [excluded]",
        symbol, realized_pnl, len(open_buys), len(open_sells),
    )
    return realized_pnl

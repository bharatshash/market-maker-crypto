"""
    This module is used to get the account information from the exchange.
    It is used to get the account balances and the open orders.
    It is also used to get the allocations of the user for a symbol.
    
"""

import asyncio
import os
import logging

from .websocket_manager import ws_manager
from typing import Any, Optional, List, Dict

async def get_account_balances() -> Optional[Any]:
    """Get all user's account balances"""
    
    async def _get_account_balances_operation(connection: Any) -> Optional[Any]:
        response = await connection.account_status()
        
        # Check if response has data before accessing it
        if hasattr(response, 'data') and callable(response.data):
            try:
                data = response.data()
                return data
            except Exception as e:
                logging.exception(f"Error getting data from response: {e}")
                return None
        else:
            logging.error("Response does not have data")
            return None

    try:
        return await ws_manager.execute_with_retry(_get_account_balances_operation)
    except Exception as e:
        logging.exception(f"get_account_balances() error: {e}")
        return None

def extract_base_asset(symbol: str) -> str:
    for quote in ['USDT', 'BUSD', 'BTC', 'ETH']:
        if symbol.endswith(quote):
            return symbol[:-len(quote)]
    return symbol  # fallback if no known quote asset

async def has_buy_position(symbol: str) -> bool:
    """Check if there's an active position on the buy side for the given symbol"""
    balances = await get_account_balances()

    if balances is None:
        return False
    
    # Extract base asset from symbol (e.g., 'BTC' from 'BTCUSDT')
    # This is a simple approach - might need refinement based on actual symbol formats
    base_asset = extract_base_asset(symbol)

    # Check if we have any balance of the base asset

    result = balances.result
    if hasattr(result, 'balances'):
        for balance in result.balances:
            if balance.asset == base_asset:
                free_balance = float(balance.free)
                locked_balance = float(balance.locked)
                total_balance = free_balance + locked_balance
                
                # Consider position exists if total balance > 0
                if total_balance > 0:
                    logging.info(f"Found active BUY position for {symbol}: {total_balance} {base_asset}")
                    return True
    
    logging.info(f"No active BUY position found for {symbol}")
    return False

async def get_open_orders(symbol: str) -> Any:
    """Get all open orders for a symbol and return the data"""

    async def _get_open_orders_operation(connection: Any, symbol: str) -> Any:
        response = await connection.open_orders_status(
            symbol=symbol
        )

        # Check rate limits first
        if hasattr(response, 'rate_limits'):
            rate_limits = response.rate_limits
            # logging.info(f"open_orders_status() rate limits: {rate_limits}")

        # Check if response has data before accessing it
        if hasattr(response, 'data') and callable(response.data):
            try:
                data = response.data()
                return data
            except Exception as e:
                logging.exception(f"Error getting data from open_orders response: {e}")
                return []
        else:
            logging.error("Open orders response does not have value for data")
            return []
            
    try:        
        return await ws_manager.execute_with_retry(_get_open_orders_operation, symbol)

    except Exception as e:
        logging.exception(f"get_open_orders() connection error: {e}")
        return []

async def has_active_orders(symbol: str, side: str) -> bool:
    """Check if there are any active BUY orders for the given symbol"""
    
    logging.info(f"Checking for active {side} orders for {symbol}...")
    open_orders = await get_open_orders(symbol)

    if open_orders is None:
        return False
    
    # If it's a list, check length directly
    if isinstance(open_orders, list):
        if len(open_orders) == 0:
            return False
        orders_to_check = open_orders
    # If it's a dict, look for orders in common keys
    elif isinstance(open_orders, dict):
        # Try common keys where orders might be stored
        orders_to_check = open_orders.get('orders', open_orders.get('data', []))
        if not isinstance(orders_to_check, list):
            orders_to_check = []
        if len(orders_to_check) == 0:
            return False
    else:
        # If it's neither list nor dict, try to get length if possible
        try:
            if hasattr(open_orders, '__len__') and len(open_orders) == 0:
                return False
            # If it's an object with an orders attribute
            if hasattr(open_orders, 'orders'):
                orders_to_check = open_orders.orders
            else:
                # Log the type for debugging
                logging.warning(f"Unexpected open_orders type: {type(open_orders)}")
                return False
        except TypeError:
            logging.error(f"Cannot check length of open_orders type: {type(open_orders)}")
            return False
    
    # Check if any of the open orders are BUY orders
    for order in orders_to_check:
        if isinstance(order, dict) and order.get('side') == side:
            logging.info(f"Found active {side} order for {symbol}: {order}")
            return True
    
    return False

async def has_sell_position(symbol: str) -> bool:
    """Check if there's a position on the sell side for the given symbol"""

    balances = await get_account_balances()

    base_asset = extract_base_asset(symbol)
    
    if balances is None:
        return False
    
    result = balances.result

    if hasattr(result, 'balances'):
        for balance in result.balances:
            if balance.asset == base_asset:
                free_balance = float(balance.free)
                locked_balance = float(balance.locked)
                total_balance = free_balance + locked_balance
                
                # Consider position exists if total balance > 0
                if total_balance > 0:
                    logging.info(f"Found active SELL position for {symbol}: {total_balance} {base_asset}")
                    return True

    logging.info(f"No active SELL position found for {symbol}")
    return False

async def get_account_info() -> Optional[Any]:
    """
    Get account information using the shared WebSocket connection
    """
    async def _get_account_info_operation(connection: Any) -> Optional[Any]:
        response = await connection.account_status()
        
        # Check if response has data before accessing it
        if hasattr(response, 'data') and callable(response.data):
            try:
                data = response.data()
                logging.info(f"account_status() response: {data}")
                return data
            except Exception as e:
                logging.exception(f"Error getting data from get_account_info response: {e}")
                return None
        else:
            logging.error("Account info response does not have data value")
            return None

    try:
        return await ws_manager.execute_with_retry(_get_account_info_operation)
    except Exception as e:
        logging.exception(f"get_account_info() error: {e}")
        return None

async def allocation(symbol: str) -> Optional[Any]:
    """Get all the user's allocations for a symbol"""
    async def _allocation_operation(connection: Any, symbol: str) -> Optional[Any]:
        response = await connection.my_allocations(
            symbol=symbol,
        )


        # Check if response has data before accessing it
        if hasattr(response, 'data') and callable(response.data):
            try:
                data = response.data()
                return data
            except Exception as e:
                logging.exception(f"Error getting data from allocation response: {e}")
                return None
        else:
            logging.error("Allocation response does not have data value")
            return None

    try:
        return await ws_manager.execute_with_retry(
            _allocation_operation, 
            symbol
        )
    except Exception as e:
        logging.exception(f"allocation() error: {e}")
        return None


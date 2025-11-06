import asyncio
import os
import logging

from .websocket_manager import ws_manager

async def get_account_balances():
    """
    Get account balances using the shared WebSocket connection
    """
    async def _get_account_balances_operation(connection):
        response = await connection.account_status()
        data = response.data()
        # logging.info(f"account_status() response: {data}")
        return data

    try:
        return await ws_manager.execute_with_retry(_get_account_balances_operation)
    except Exception as e:
        logging.error(f"get_account_balances() error: {e}")
        return None

async def has_buy_position(symbol):
    """Check if there's an active position on the buy side for the given symbol
    This checks if we have a non-zero balance of the base asset"""
    balances = await get_account_balances()
    
    if balances is None:
        return False
    
    # Extract base asset from symbol (e.g., 'BTC' from 'BTCUSDT')
    # This is a simple approach - might need refinement based on actual symbol formats
    base_asset = symbol.replace('USDT', '').replace('BUSD', '').replace('BTC', '').replace('ETH', '')
    
    # Check if we have any balance of the base asset
    if 'balances' in balances:
        for balance in balances['balances']:
            if balance.get('asset') == base_asset:
                free_balance = float(balance.get('free', 0))
                locked_balance = float(balance.get('locked', 0))
                total_balance = free_balance + locked_balance
                
                # Consider position exists if total balance > 0
                if total_balance > 0:
                    return True
    
    return False

async def get_open_orders(symbol):
    """Get all open orders for a symbol and return the data"""

    async def _get_open_orders_operation(connection, symbol):
        response = await connection.open_orders_status(
            symbol=symbol
        )

        rate_limits = response.rate_limits
        logging.info(f"open_orders_status() rate limits: {rate_limits}")

        data = response.data()
        logging.info(f"open_orders_status() response: {data}")
        return data
    try:        
        return await ws_manager.execute_with_retry(_get_open_orders_operation, symbol)

    except Exception as e:
        logging.error(f"get_open_orders() connection error: {e}")
        return None

async def has_active_buy_orders(symbol):
    """Check if there are any active BUY orders for the given symbol"""
    open_orders = asyncio.create_task(get_open_orders(symbol))
    
    if open_orders is None:
        return False
    
    # Check if any of the open orders are BUY orders
    for order in open_orders:
        if order.get('side') == 'BUY':
            return True
    
    return False


async def has_active_sell_orders(symbol):
    """Check if there are any active SELL orders for the given symbol"""
    open_orders = await get_open_orders(symbol)
    
    if open_orders is None:
        return False
    
    # Check if any of the open orders are SELL orders
    for order in open_orders:
        if order.get('side') == 'SELL':
            return True
    
    return False

async def get_account_info():
    """
    Get account information using the shared WebSocket connection
    """
    async def _get_account_info_operation(connection):
        response = await connection.account_status()
        data = response.data()
        logging.info(f"account_status() response: {data}")
        
        balance = response
        logging.info(f"account_status() balances: {balance}")
        return data

    try:
        return await ws_manager.execute_with_retry(_get_account_info_operation)
    except Exception as e:
        logging.error(f"get_account_info() error: {e}")
        return None

async def allocation(symbol):
    """
    Get allocations for a symbol using the shared WebSocket connection
    """
    async def _allocation_operation(connection, symbol):
        response = await connection.my_allocations(
            symbol=symbol,
        )

        rate_limits = response.rate_limits
        logging.info(f"my_allocations() rate limits: {rate_limits}")

        data = response.data()
        logging.info(f"my_allocations() response: {data}")
        return data

    try:
        return await ws_manager.execute_with_retry(
            _allocation_operation, 
            symbol
        )
    except Exception as e:
        logging.error(f"allocation() error: {e}")
        return None


  try:
        # has_buy_orders = asyncio.create_task(has_active_buy_orders(symbol))
        # has_buy_pos = asyncio.create_task(has_buy_position(symbol))

        has_buy_orders = await has_active_buy_orders(symbol)
        has_buy_pos = await has_buy_position(symbol)

        # If no active buy order and no active position on buy side
        if not has_buy_orders and not has_buy_pos:
            # Compute buy price: bid_price = best_bid - buy_offset
            bid_price = best_bid - BUY_OFFSET
            
            print(f"No active buy order and no buy position detected for {symbol}")
            print(f"Placing buy order at {bid_price} (best_bid: {best_bid}, offset: {BUY_OFFSET})")
            
            # Place limit buy order
            await place_order(
                symbol=symbol, 
                side='BUY', 
                price=bid_price, 
                quantity=DEFAULT_QUANTITY, 
                order_type='LIMIT', 
                timeInForce='GTC'
            )
        else:
            if has_buy_orders:
                print(f"Active buy orders exist for {symbol}, skipping buy order placement")
                # Check for market proximity to existing buy orders here (not implemented)
            if has_buy_pos:
                print(f"Active buy position exists for {symbol}, skipping buy order placement")
                
    except Exception as e:
        print(f"Error checking orders/positions or placing buy order: {e}")
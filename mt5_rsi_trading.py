import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    if len(prices) < period + 1:
        # Not enough data to calculate RSI properly
        return 50  # Return neutral RSI if insufficient data
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
    
    return rsi

def main():
    # Initialize MT5 connection
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        return
    
    print("MT5 initialized successfully")
    
    # Define symbol (you can change this to any symbol you want to trade)
    symbol = "EURUSD"  # You can modify this as needed
    
    # Check if the symbol exists
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select {symbol}")
        mt5.shutdown()
        return
    
    while True:
        try:
            # Get the last 12 candles in 1-minute timeframe
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 12)
            
            if rates is None or len(rates) < 12:
                print("Not enough data to analyze")
                time.sleep(60)  # Wait 1 minute before next attempt
                continue
            
            # Extract closing prices for RSI calculation
            closes = rates['close']
            
            # Calculate RSI for each of the last 12 candles
            rsis = []
            for i in range(1, min(13, len(closes)+1)):  # Go back up to 12 candles
                recent_closes = closes[max(0, len(closes)-i-13):len(closes)-i+1]
                if len(recent_closes) >= 14:  # Need at least 14 data points for RSI
                    rsi_value = calculate_rsi(recent_closes)
                    rsis.append(rsi_value)
            
            # We only care about the last 3 RSIs (most recent)
            recent_rsis = rsis[-3:] if len(rsis) >= 3 else rsis
            
            if len(recent_rsis) < 3:
                print("Not enough RSI values calculated")
                time.sleep(60)
                continue
            
            # Count how many of the last 3 RSIs are less than 38
            rsi_less_than_38 = sum(1 for rsi in recent_rsis if rsi < 38)
            rsi_more_than_65 = sum(1 for rsi in recent_rsis if rsi > 65)
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            current_price = tick.ask  # Using ask price for buying
            
            # Get positions to check if we already have open trades
            positions = mt5.positions_get(symbol=symbol)
            
            # Check for buy condition: at least 3 of last 3 RSI values < 38
            if rsi_less_than_38 >= 3:
                # Only buy if we don't already have a position
                if positions is None or len(positions) == 0:
                    lot_size = 0.1  # Adjust lot size as needed
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": lot_size,
                        "type": mt5.ORDER_TYPE_BUY,
                        "price": current_price,
                        "slippage": 10,
                        "comment": "RSI Buy Signal",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    
                    result = mt5.order_send(request)
                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        print(f"Buy order failed, retcode: {result.retcode}")
                    else:
                        print(f"Buy order sent successfully at price: {current_price}")
                else:
                    print("Already have open position, skipping buy")
            
            # Check for sell condition: at least 3 of last 3 RSI values > 65
            elif rsi_more_than_65 >= 3 and positions is not None:
                # Check if we have a buy position and profit is at least $1
                for pos in positions:
                    if pos.type == mt5.POSITION_TYPE_BUY:  # It's a long position
                        profit = (current_price - pos.price_open) * pos.volume * mt5.symbol_info(symbol).trade_profit_calc_mode
                        # Assuming standard lot where 1 pip = $10 for major pairs (adjust as needed)
                        # Simplified profit calculation - adjust based on your symbol
                        pip_value = mt5.symbol_info(symbol).point * 10  # This might vary by symbol
                        
                        # Calculate profit in dollars (this is simplified - you might need to adjust based on symbol)
                        if current_price > pos.price_open + 0.01:  # At least $1 profit (approximate)
                            # Close the position
                            close_request = {
                                "action": mt5.TRADE_ACTION_DEAL,
                                "symbol": symbol,
                                "volume": pos.volume,
                                "type": mt5.ORDER_TYPE_SELL,
                                "position": pos.ticket,
                                "price": current_price,
                                "slippage": 10,
                                "comment": "RSI Sell Signal",
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_IOC,
                            }
                            
                            result = mt5.order_send(close_request)
                            if result.retcode != mt5.TRADE_RETCODE_DONE:
                                print(f"Sell order failed, retcode: {result.retcode}")
                            else:
                                print(f"Sell order sent successfully at price: {current_price}, profit: ${profit}")
                        else:
                            print("Position not profitable enough to close")
            
            print(f"Current Price: {current_price}, Last 3 RSIs: {recent_rsis[-3:]}")
            print(f"RSIs < 38: {rsi_less_than_38}, RSIs > 65: {rsi_more_than_65}")
            
            # Wait 1 minute before next check
            time.sleep(60)
        
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)
    
    # Shutdown MT5 connection
    mt5.shutdown()

if __name__ == "__main__":
    main()
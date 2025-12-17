# MetaTrader 5 RSI Trading Bot

This project contains a Python script that connects to MetaTrader 5 and implements an RSI-based trading strategy.

## Requirements

To run this script, you need:

1. **MetaTrader 5 Terminal** installed on your Windows machine
2. **Python 3.x** 
3. **MetaTrader5 Python package**: Install using:
   ```bash
   pip install MetaTrader5
   ```

## Features of the Trading Strategy

- Connects to MetaTrader 5
- Fetches 1-minute timeframe data for the last 12 candles
- Calculates RSI (Relative Strength Index) for each candle
- **BUY Condition**: If 3 out of the last 3 RSI values are less than 38 (oversold)
- **SELL Condition**: If 3 out of the last 3 RSI values are greater than 65 (overbought) AND the position has at least $1 profit
- Only executes one trade at a time (checks for existing positions)

## Installation

1. Install MetaTrader 5 on your Windows machine
2. Install the MetaTrader5 Python package:
   ```bash
   pip install MetaTrader5
   ```
3. Make sure your MetaTrader 5 terminal is running and logged in to your account
4. Run the script:
   ```bash
   python mt5_rsi_trading.py
   ```

## Important Notes

⚠️ **Risk Warning**: This is a trading bot that executes real trades. Use at your own risk. Always test with a demo account first.

- The default symbol is EURUSD, but you can modify it in the code
- Lot size is set to 0.1 by default, adjust according to your risk management
- The script includes basic error handling but should be enhanced for production use
- Profit calculation is approximate and may need adjustment based on the traded symbol

## How the Strategy Works

1. Every minute, the script gets the last 12 candles in 1-minute timeframe
2. It calculates the RSI for each candle using the closing prices
3. It checks the last 3 RSI values:
   - If all 3 are below 38 → Sends BUY order
   - If all 3 are above 65 → Sends SELL order (if position exists and profitable)
4. The sell condition only triggers if the position has at least $1 profit

## Customization

You can customize:
- Trading symbol (default: EURUSD)
- Lot size (default: 0.1)
- RSI thresholds (currently 38 for buy, 65 for sell)
- Timeframe (currently M1)
- Number of candles to analyze

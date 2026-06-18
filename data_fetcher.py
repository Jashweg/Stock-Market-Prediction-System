import yfinance as yf
import pandas as pd
import numpy as np

def fetch_data(ticker, start_date, end_date):
    """Fetches historical stock data from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        # yfinance returns DatetimeIndex, but timezone-aware
        if not df.empty:
            df.index = df.index.tz_localize(None)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def compute_rsi(data, window=14):
    """Computes the Relative Strength Index."""
    delta = data['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    # Exponential moving average
    ma_up = up.ewm(com=window - 1, adjust=True, min_periods=window).mean()
    ma_down = down.ewm(com=window - 1, adjust=True, min_periods=window).mean()
    
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi

def compute_macd(data, short_window=12, long_window=26, signal_window=9):
    """Computes Moving Average Convergence Divergence."""
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    macd_histogram = macd_line - signal_line
    return macd_line, signal_line, macd_histogram

def preprocess_data(df):
    """Adds technical indicators to the dataframe."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # RSI
    df['RSI_14'] = compute_rsi(df)
    
    # MACD
    macd, signal, hist = compute_macd(df)
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    df['MACD_Hist'] = hist
    
    # Daily Returns
    df['Daily_Return'] = df['Close'].pct_change()
    
    # Target Variable: 1 if the price goes UP tomorrow, 0 if it goes DOWN or stays same
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    # Drop NaNs that were introduced by rolling windows and shifting
    df.dropna(inplace=True)
    
    return df

"""
Technical indicators for Portfolio Tracker.
ADX(14), SMA20, SMA200, BB, Donchian calculations from OHLCV data.
ADX menggunakan Wilder's Smoothing via EWM (sama persis dengan stocktrade).
"""

import numpy as np
import pandas as pd


def calculate_adx(df: pd.DataFrame, period: int = 14) -> tuple:
    """
    Calculate ADX(14), +DI (PDI), -DI (MDI) menggunakan Wilder's Smoothing via EWM.
    
    Returns (adx_series, pdi_series, mdi_series) aligned with df index.
    """
    high = df['High'].astype(float)
    low = df['Low'].astype(float)
    close = df['Close'].astype(float)

    # True Range
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    # Directional Movement (+DM / -DM)
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0), index=df.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0), index=df.index)

    # Wilder's Smoothing via EWM (alpha = 1/period)
    alpha = 1.0 / period
    smoothed_tr = tr.ewm(alpha=alpha, adjust=False, min_periods=period).mean()
    smoothed_plus = plus_dm.ewm(alpha=alpha, adjust=False, min_periods=period).mean()
    smoothed_minus = minus_dm.ewm(alpha=alpha, adjust=False, min_periods=period).mean()

    # +DI / -DI (PDI / MDI)
    pdi = 100 * smoothed_plus / smoothed_tr.replace(0, np.nan)
    mdi = 100 * smoothed_minus / smoothed_tr.replace(0, np.nan)

    # DX
    dm_sum = pdi + mdi
    dx = 100 * (pdi - mdi).abs() / dm_sum.replace(0, np.nan)

    # ADX = smoothed DX
    adx = dx.ewm(alpha=alpha, adjust=False, min_periods=period).mean()

    return adx, pdi, mdi


def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=period).mean()


def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20) -> tuple:
    """
    Calculate Bollinger Bands (SMA20 as middle band).
    Returns (upper_bb, middle_bb, lower_bb).
    """
    close = df['Close']
    sma = calculate_sma(close, period)
    std = close.rolling(window=period).std()
    upper = sma + (std * 2)
    lower = sma - (std * 2)
    return upper, sma, lower


def calculate_donchian(df: pd.DataFrame, period: int = 20) -> tuple:
    """
    Donchian Channel.
    Returns (upper, middle, lower) channels.
    """
    upper = df['High'].rolling(window=period).max()
    lower = df['Low'].rolling(window=period).min()
    middle = (upper + lower) / 2
    return upper, middle, lower


def calculate_sl(df: pd.DataFrame, atr_multiple: float = 2.8, atr_period: int = 10) -> pd.Series:
    """
    Donchian Stop Loss — ported from stocktrade ``calculate_sl()``.
    
    Logic (sama persis dengan EA MT4 & stocktrade):
      ero = atr_multiple * atr_period             # 2.8 x 10 = 28
      r = highest(high, ero)                      # Upper channel
      s = lowest(low, ero)                        # Lower channel
      ab = high > r[1] ? 1 : (low < s[1] ? -1 : 0)
      ac = valuewhen(ab != 0, ab, 0) (forward-filled)
      sl = ac == 1 ? s : r
      
    Uptrend (ac=1):    sl = lower channel (s)  → trailing stop naik
    Downtrend (ac=-1): sl = upper channel (r)  → trailing stop turun
    
    Returns pd.Series aligned with df.index.
    """
    high = df['High'].astype(float)
    low = df['Low'].astype(float)
    
    ero = int(atr_multiple * atr_period)
    
    # Donchian dengan shift(1) untuk hindari look-ahead
    r_prev = high.rolling(window=ero).max().shift(1)
    s_prev = low.rolling(window=ero).min().shift(1)
    r_curr = high.rolling(window=ero).max()
    s_curr = low.rolling(window=ero).min()
    
    # Trigger arah: ab
    ab = np.where(high > r_prev, 1,
                  np.where(low < s_prev, -1, 0))
    
    # Direction persistence: ac = valuewhen(ab != 0, ab, 0)
    ac = pd.Series(ab).replace(0, np.nan).ffill().fillna(0).values
    
    # SL = ac == 1 ? lower_channel : upper_channel
    sl = np.where(ac == 1, s_curr, r_curr)
    
    return pd.Series(sl, index=df.index)

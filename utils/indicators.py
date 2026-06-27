"""
Technical indicators for Portfolio Tracker.
ADX(14), SMA20, SMA200 calculations from OHLCV data.
"""

import numpy as np
import pandas as pd


def calculate_adx(df: pd.DataFrame, period: int = 14) -> tuple:
    """
    Calculate ADX(14), +DI, -DI from OHLCV DataFrame.
    
    Returns (adx_series, pdi_series, mdi_series) aligned with df index.
    """
    high = df['High'].values.astype(float)
    low = df['Low'].values.astype(float)
    close = df['Close'].values.astype(float)
    n = len(df)

    up_move = np.zeros(n)
    down_move = np.zeros(n)

    for i in range(1, n):
        up_move[i] = high[i] - high[i - 1]
        down_move[i] = low[i - 1] - low[i]

    # True Range
    tr = np.zeros(n)
    for i in range(1, n):
        tr[i] = max(
            high[i] - low[i],
            abs(high[i] - close[i - 1]),
            abs(low[i] - close[i - 1]),
        )

    # Smoothed averages (Wilder's method)
    def wilder_smooth(values, period):
        smoothed = np.zeros(n)
        smoothed[:period] = np.nan
        smoothed[period] = np.sum(values[1 : period + 1])  # first sum
        for i in range(period + 1, n):
            smoothed[i] = smoothed[i - 1] - (smoothed[i - 1] / period) + values[i]
        return smoothed

    atr = wilder_smooth(tr, period)
    up_smooth = wilder_smooth(up_move, period)
    down_smooth = wilder_smooth(down_move, period)

    pdi = np.zeros(n) * np.nan
    mdi = np.zeros(n) * np.nan
    dx = np.zeros(n) * np.nan

    for i in range(period, n):
        if atr[i] != 0:
            pdi[i] = (up_smooth[i] / atr[i]) * 100
            mdi[i] = (down_smooth[i] / atr[i]) * 100
        if (pdi[i] + mdi[i]) != 0:
            dx[i] = abs(pdi[i] - mdi[i]) / (pdi[i] + mdi[i]) * 100

    adx = np.zeros(n) * np.nan
    adx_start = period * 2
    if adx_start < n:
        adx[adx_start] = np.nanmean(dx[period : period * 2])
        for i in range(adx_start + 1, n):
            if not np.isnan(adx[i - 1]) and not np.isnan(dx[i]):
                adx[i] = (adx[i - 1] * (period - 1) + dx[i]) / period

    return (
        pd.Series(adx, index=df.index),
        pd.Series(pdi, index=df.index),
        pd.Series(mdi, index=df.index),
    )


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

"""
Trend Analysis menggunakan framework ADX(14) + SMA20.
Diadaptasi dari stocktrade — identical logic.
"""

import numpy as np


def calculate_trend_analysis(data, adx_series, pdi_series, mdi_series, middle_bb):
    """
    Trend Analysis menggunakan framework ADX(14) + SMA20.
    Menghitung persentase bar bullish (ADX>25 + Close>SMA20) dan bearish (ADX>25 + Close<SMA20).
    
    Threshold:
      - Strong Bullish: >35% bar ADX>25 dan Close>SMA20
      - Weak Bullish: 30-35%
      - Sideway: <30%
      - Weak Bearish: 30-35% ADX>25 dan Close<SMA20
      - Strong Bearish: >35%
    
    Returns dict dengan trend stats lengkap.
    """
    n = len(data)
    start_idx = 20
    sma20 = middle_bb

    valid_bars = 0
    bull_bars = 0
    bear_bars = 0
    sideway_bars = 0

    adx_brackets = {
        '0_20': {'count': 0, 'above_sma': 0, 'label': 'ADX 0-20 (No trend)'},
        '20_25': {'count': 0, 'above_sma': 0, 'label': 'ADX 20-25 (Weak trend)'},
        '25_40': {'count': 0, 'above_sma': 0, 'label': 'ADX 25-40 (Strong trend)'},
        '40_999': {'count': 0, 'above_sma': 0, 'label': 'ADX 40+ (Very strong)'},
    }

    for i in range(start_idx, n):
        if np.isnan(adx_series.iloc[i]) or np.isnan(sma20.iloc[i]):
            continue
        valid_bars += 1
        close = float(data['Close'].iloc[i])
        sma = float(sma20.iloc[i])
        adx_val = float(adx_series.iloc[i])

        if adx_val > 25:
            if close > sma:
                bull_bars += 1
            else:
                bear_bars += 1
        else:
            sideway_bars += 1

        if adx_val <= 20:
            bracket = '0_20'
        elif adx_val <= 25:
            bracket = '20_25'
        elif adx_val <= 40:
            bracket = '25_40'
        else:
            bracket = '40_999'
        adx_brackets[bracket]['count'] += 1
        if close > sma:
            adx_brackets[bracket]['above_sma'] += 1

    if valid_bars == 0:
        return {'valid_bars': 0, 'error': 'No valid data'}

    bull_pct = (bull_bars / valid_bars) * 100
    bear_pct = (bear_bars / valid_bars) * 100
    sideway_pct = (sideway_bars / valid_bars) * 100

    if bull_pct > 35:
        classification = 'STRONG BULLISH'
        class_icon = chr(0x1f4c8)
    elif bull_pct >= 30:
        classification = 'WEAK BULLISH'
        class_icon = chr(0x2197) + chr(0xfe0f)
    elif bear_pct > 35:
        classification = 'STRONG BEARISH'
        class_icon = chr(0x1f4c9)
    elif bear_pct >= 30:
        classification = 'WEAK BEARISH'
        class_icon = chr(0x2198) + chr(0xfe0f)
    else:
        classification = 'SIDEWAYS'
        class_icon = chr(0x27a1) + chr(0xfe0f)

    # ── Multi-window trend analysis ──
    # Last 100 bars
    last100_start = max(start_idx, n - 100)
    last100_valid = 0
    last100_bull = 0
    last100_bear = 0
    for i in range(last100_start, n):
        if np.isnan(adx_series.iloc[i]) or np.isnan(sma20.iloc[i]):
            continue
        last100_valid += 1
        close = float(data['Close'].iloc[i])
        sma = float(sma20.iloc[i])
        adx_val = float(adx_series.iloc[i])
        if adx_val > 25:
            if close > sma:
                last100_bull += 1
            else:
                last100_bear += 1

    last100_bull_pct = (last100_bull / last100_valid * 100) if last100_valid > 0 else 0
    last100_bear_pct = (last100_bear / last100_valid * 100) if last100_valid > 0 else 0

    # Last 200 bars
    last200_start = max(start_idx, n - 200)
    last200_valid = 0
    last200_bull = 0
    last200_bear = 0
    for i in range(last200_start, n):
        if np.isnan(adx_series.iloc[i]) or np.isnan(sma20.iloc[i]):
            continue
        last200_valid += 1
        close = float(data['Close'].iloc[i])
        sma = float(sma20.iloc[i])
        adx_val = float(adx_series.iloc[i])
        if adx_val > 25:
            if close > sma:
                last200_bull += 1
            else:
                last200_bear += 1

    last200_bull_pct = (last200_bull / last200_valid * 100) if last200_valid > 0 else 0
    last200_bear_pct = (last200_bear / last200_valid * 100) if last200_valid > 0 else 0

    def trend_interpretation(bull_pct, bear_pct):
        if bull_pct > 35:
            return 'Strong Bullish', '#4ade80', chr(0x1f4c8)
        elif bull_pct >= 25:
            return 'Weak Bullish', '#a3e635', chr(0x2197) + chr(0xfe0f)
        elif bear_pct > 35:
            return 'Strong Bearish', '#f87171', chr(0x1f4c9)
        elif bear_pct >= 25:
            return 'Weak Bearish', '#fb923c', chr(0x2198) + chr(0xfe0f)
        else:
            return 'Sideways', '#fbbf24', chr(0x27a1) + chr(0xfe0f)

    total_class, total_color, total_icon = trend_interpretation(bull_pct, bear_pct)
    if classification == 'STRONG BULLISH':
        total_class = 'STRONG BULLISH'
    elif classification == 'WEAK BULLISH':
        total_class = 'WEAK BULLISH'
    elif classification == 'STRONG BEARISH':
        total_class = 'STRONG BEARISH'
    elif classification == 'WEAK BEARISH':
        total_class = 'WEAK BEARISH'
    else:
        total_class = 'SIDEWAYS'

    l100_class, l100_color, l100_icon = trend_interpretation(last100_bull_pct, last100_bear_pct)
    l200_class, l200_color, l200_icon = trend_interpretation(last200_bull_pct, last200_bear_pct)

    # Override with stricter thresholds
    if last100_bull_pct > 35:
        last100_class = 'STRONG BULLISH'
    elif last100_bull_pct >= 30:
        last100_class = 'WEAK BULLISH'
    elif last100_bear_pct > 35:
        last100_class = 'STRONG BEARISH'
    elif last100_bear_pct >= 30:
        last100_class = 'WEAK BEARISH'
    else:
        last100_class = 'SIDEWAYS'

    trend_windows = [
        {
            'label': 'Last 100 bars',
            'bars': last100_valid,
            'bull_pct': round(last100_bull_pct, 1),
            'bear_pct': round(last100_bear_pct, 1),
            'sideway_pct': round(100 - last100_bull_pct - last100_bear_pct, 1),
            'classification': l100_class,
            'color': l100_color,
        },
        {
            'label': 'Last 200 bars',
            'bars': last200_valid,
            'bull_pct': round(last200_bull_pct, 1),
            'bear_pct': round(last200_bear_pct, 1),
            'sideway_pct': round(100 - last200_bull_pct - last200_bear_pct, 1),
            'classification': l200_class,
            'color': l200_color,
        },
        {
            'label': f'All ({valid_bars} bars)',
            'bars': valid_bars,
            'bull_pct': round(bull_pct, 1),
            'bear_pct': round(bear_pct, 1),
            'sideway_pct': round(sideway_pct, 1),
            'classification': total_class,
            'color': total_color,
        },
    ]

    # Current status values
    last_close = float(data['Close'].iloc[-1])
    last_sma20 = float(sma20.iloc[-1])
    last_adx_val = float(adx_series.iloc[-1])
    last_pdi = float(pdi_series.iloc[-1])
    last_mdi = float(mdi_series.iloc[-1])
    sma20_dist = ((last_close / last_sma20) - 1) * 100

    return {
        'valid_bars': valid_bars,
        'classification': classification,
        'class_icon': class_icon,
        'bull_pct': round(bull_pct, 1),
        'bear_pct': round(bear_pct, 1),
        'sideway_pct': round(sideway_pct, 1),
        'last100_valid': last100_valid,
        'last100_class': last100_class,
        'last100_bull_pct': round(last100_bull_pct, 1),
        'last100_bear_pct': round(last100_bear_pct, 1),
        'current': {
            'close': round(last_close, 2),
            'sma20': round(last_sma20, 2),
            'sma20_dist': round(sma20_dist, 2),
            'adx': round(last_adx_val, 1),
            'pdi': round(last_pdi, 1),
            'mdi': round(last_mdi, 1),
            'above_sma20': last_close > last_sma20,
            'pdi_above_mdi': last_pdi > last_mdi,
            'adx_above_25': last_adx_val > 25,
        },
        'trend_windows': trend_windows,
        'adx_brackets': adx_brackets,
    }


def calculate_adx_sma_pct(data, adx_series, pdi_series, mdi_series, middle_bb, window=100):
    """
    Hitung persentase bar di mana ADX > 25 AND Close > SMA20 (Basis)
    dalam window bar terakhir (default: 100).

    Returns:
        (adx_sma_pct, trend_commentary)
    """
    valid_count = 0
    adx_sma_count = 0
    n = len(data)
    start = max(20, n - window)

    for i in range(start, n):
        if np.isnan(adx_series.iloc[i]):
            continue
        valid_count += 1
        close = float(data['Close'].iloc[i])
        sma20 = float(middle_bb.iloc[i])
        adx = float(adx_series.iloc[i])
        if adx > 25 and close > sma20:
            adx_sma_count += 1

    pct = (adx_sma_count / valid_count * 100) if valid_count > 0 else 0.0

    if pct >= 35:
        commentary = f"Uptrend Kuat ({pct:.0f}%)"
    elif pct >= 30:
        commentary = f"Medium Uptrend ({pct:.0f}%)"
    else:
        commentary = f"Sideways ({pct:.0f}%)"

    return round(pct, 1), commentary

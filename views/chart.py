"""
Chart routes — Bokeh interactive chart page per ticker.
Supports timeframe switching: 1h, 4h, 1d (default), 1wk, 1mo.
"""

from flask import Blueprint, render_template, flash, request
from flask_login import login_required
import yfinance as yf
import pandas as pd
import numpy as np
import time

from utils.indicators import calculate_adx, calculate_sma, calculate_bollinger_bands, calculate_donchian
from utils.trend_analysis import calculate_trend_analysis, calculate_adx_sma_pct
from utils.bokeh_chart import generate_chart
from bokeh.resources import CDN

chart_bp = Blueprint('chart', __name__)

# ── Timeframe config ──────────────────────────────────────────
TIMEFRAMES = {
    '1h':  {'interval': '1h',  'period': '30d',  'resample': None,      'label': 'H1',  'bars_label': '1h bars'},
    '4h':  {'interval': '1h',  'period': '60d',  'resample': '4h',      'label': 'H4',  'bars_label': '4h bars'},
    '1d':  {'interval': '1d',  'period': '2y',   'resample': None,      'label': 'D1',  'bars_label': 'daily bars'},
    '1wk': {'interval': '1wk', 'period': '5y',   'resample': None,      'label': 'W1',  'bars_label': 'weekly bars'},
    '1mo': {'interval': '1mo', 'period': '10y',  'resample': None,      'label': 'MN',  'bars_label': 'monthly bars'},
}
DEFAULT_TF = '1d'


def _fetch_data(ticker, tf_config):
    """Download and optionally resample data based on timeframe config."""
    interval = tf_config['interval']
    period = tf_config['period']
    resample = tf_config['resample']

    t = yf.Ticker(ticker)
    df = t.history(period=period, interval=interval)

    if df.empty or len(df) < 30:
        return df

    # Capitalize columns
    df.columns = [c.capitalize() for c in df.columns]

    # Resample for 4h
    if resample:
        ohlc_dict = {
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum',
        }
        # Keep only needed columns
        cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        df_resampled = df[cols].resample(resample, label='right', closed='right').agg(ohlc_dict)
        df_resampled = df_resampled.dropna()
        if len(df_resampled) >= 30:
            df = df_resampled
        # else keep original 1h data if resample too short

    return df


@chart_bp.route('/chart/<ticker>')
@login_required
def chart_view(ticker):
    """
    Show interactive Bokeh chart + trend analysis for a ticker.
    Supports ?tf=1h|4h|1d|1wk|1mo (default: 1d).
    """
    start_time = time.time()

    # ── Detect timeframe ──
    tf = request.args.get('tf', DEFAULT_TF)
    if tf not in TIMEFRAMES:
        tf = DEFAULT_TF
    tf_config = TIMEFRAMES[tf]

    try:
        df = _fetch_data(ticker, tf_config)

        if df.empty or len(df) < 30:
            flash(f'Insufficient data for {ticker} on {tf_config["label"]} ({len(df)} bars).', 'error')
            return render_template('chart.html', ticker=ticker, error=True, tf=tf, tf_label=tf_config['label'])

        # Calculate indicators
        adx_series, pdi_series, mdi_series = calculate_adx(df)
        df['ADX'] = adx_series
        df['+DI'] = pdi_series
        df['-DI'] = mdi_series

        upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(df, period=20)
        df['SMA20'] = middle_bb
        df['BB_upper'] = upper_bb
        df['BB_lower'] = lower_bb
        df['SMA200'] = calculate_sma(df['Close'], 200)

        # Donchian Channel (SL)
        donchian_upper, donchian_mid, donchian_lower = calculate_donchian(df, period=20)
        df['Donchian_lower'] = donchian_lower

        # Trend analysis
        ta = calculate_trend_analysis(df, adx_series, pdi_series, mdi_series, middle_bb)
        adx_pct, adx_commentary = calculate_adx_sma_pct(df, adx_series, pdi_series, mdi_series, middle_bb)

        # Generate Bokeh chart
        chart_script, chart_div = generate_chart(ticker.upper(), df)

        duration = round((time.time() - start_time) * 1000)

        return render_template(
            'chart.html',
            ticker=ticker.upper(),
            chart_script=chart_script,
            chart_div=chart_div,
            ta=ta,
            adx_pct=adx_pct,
            adx_commentary=adx_commentary,
            bars=len(df),
            duration=duration,
            error=False,
            bokeh_cdn=CDN.render(),
            tf=tf,
            tf_label=tf_config['label'],
            bars_label=tf_config['bars_label'],
        )

    except Exception as e:
        flash(f'Failed to load data for {ticker}: {str(e)}', 'error')
        return render_template('chart.html', ticker=ticker, error=True, tf=tf)

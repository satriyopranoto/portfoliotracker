"""
Chart routes — Bokeh interactive chart page per ticker.
"""

from flask import Blueprint, render_template, flash
from flask_login import login_required
import yfinance as yf
import pandas as pd
import numpy as np
import time

from utils.indicators import calculate_adx, calculate_sma, calculate_bollinger_bands
from utils.trend_analysis import calculate_trend_analysis, calculate_adx_sma_pct
from utils.bokeh_chart import generate_chart
from bokeh.resources import CDN

chart_bp = Blueprint('chart', __name__)


@chart_bp.route('/chart/<ticker>')
@login_required
def chart_view(ticker):
    """
    Show interactive Bokeh chart + trend analysis for a ticker.
    Fetches ~2 years of daily data from Yahoo Finance.
    """
    start_time = time.time()

    try:
        # Fetch data
        t = yf.Ticker(ticker)
        df = t.history(period='2y')

        if df.empty or len(df) < 30:
            flash(f'Data tidak mencukupi untuk {ticker} (< 30 bar).', 'error')
            return render_template('chart.html', ticker=ticker, error=True)

        # Ensure column names match expectations
        df.columns = [c.capitalize() for c in df.columns]

        # Calculate indicators
        adx_series, pdi_series, mdi_series = calculate_adx(df)
        df['ADX'] = adx_series
        df['+DI'] = pdi_series
        df['-DI'] = mdi_series

        upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(df, period=20)
        df['SMA20'] = middle_bb
        df['SMA200'] = calculate_sma(df['Close'], 200)

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
        )

    except Exception as e:
        flash(f'Gagal memuat data untuk {ticker}: {str(e)}', 'error')
        return render_template('chart.html', ticker=ticker, error=True)

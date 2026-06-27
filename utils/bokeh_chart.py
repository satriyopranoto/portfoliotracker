"""
Bokeh interactive chart module for Portfolio Tracker.
Generates candlestick + BB + Donchian SL + ADX chart with interactive tools.
Uses components() for embedding in Jinja2 templates.
"""

import numpy as np
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import (
    ColumnDataSource,
    CrosshairTool,
    HoverTool,
    Span,
    NumeralTickFormatter,
    Range1d,
    FixedTicker,
)

# ── Color scheme (dark theme) ──────────────────────────────
COLORS = {
    "bg": "#1a1612",
    "border": "#2d2a21",
    "text": "#eae1d4",
    "grid": "#2d2a21",
    "up": "#4ade80",
    "down": "#f87171",
    "wick": "#99907c",
    "sl": "#fb923c",
    "adx": "#a78bfa",
    "pdi": "#4ade80",
    "mdi": "#f87171",
    "sma20": "#60a5fa",
    "sma200": "#fbbf24",
    "bb_upper": "#6b7280",
    "bb_lower": "#6b7280",
    "bb_fill": "#6b7280",
    "donchian": "#fb923c",
    "ref_line": "#555555",
    "legend_text": "#eae1d4",
    "volume": "#555555",
}


def _make_base_figure(**kwargs):
    """Create a base Bokeh figure with shared dark theme styling."""
    defaults = dict(
        background_fill_color=COLORS["bg"],
        border_fill_color=COLORS["bg"],
        outline_line_color=COLORS["border"],
        toolbar_location="above",
        toolbar_sticky=False,
        tools="pan,box_zoom,wheel_zoom,reset,save",
        active_scroll="wheel_zoom",
        y_axis_location="right",
    )
    defaults.update(kwargs)
    p = figure(**defaults)
    p.xgrid.grid_line_color = COLORS["grid"]
    p.ygrid.grid_line_color = COLORS["grid"]
    p.xgrid.grid_line_alpha = 0.5
    p.ygrid.grid_line_alpha = 0.5
    # Axis styling
    p.axis.major_label_text_color = COLORS["text"]
    p.axis.major_label_text_font_size = "10px"
    p.axis.axis_label_text_color = COLORS["text"]
    p.axis.axis_line_color = COLORS["border"]
    p.axis.major_tick_line_color = COLORS["border"]
    p.axis.minor_tick_line_color = COLORS["border"]
    # Title
    p.title.text_color = COLORS["text"]
    p.title.text_font_size = "14px"
    p.title.text_font_style = "bold"
    return p


def _candlestick_figure(p, df):
    """Draw candlestick bars, SMA20, SMA200 on figure p."""
    up_mask = df["Close"] >= df["Open"]
    down_mask = ~up_mask

    df_up = df[up_mask]
    df_down = df[down_mask]

    mid_up = (df_up["Open"] + df_up["Close"]) / 2
    height_up = (df_up["Close"] - df_up["Open"]).clip(lower=0.001)

    mid_down = (df_down["Open"] + df_down["Close"]) / 2
    height_down = (df_down["Open"] - df_down["Close"]).clip(lower=0.001)

    src_up = ColumnDataSource(dict(
        idx=df_up["idx"], high=df_up["High"], low=df_up["Low"],
        mid=mid_up, height=height_up,
    ))
    src_down = ColumnDataSource(dict(
        idx=df_down["idx"], high=df_down["High"], low=df_down["Low"],
        mid=mid_down, height=height_down,
    ))

    # Wicks
    p.segment("idx", "high", "idx", "low", source=src_up, color=COLORS["up"], line_width=1)
    p.segment("idx", "high", "idx", "low", source=src_down, color=COLORS["down"], line_width=1)

    # Body
    p.rect("idx", "mid", 0.7, "height", source=src_up,
           fill_color=COLORS["up"], line_color=COLORS["up"], line_width=0.5)
    p.rect("idx", "mid", 0.7, "height", source=src_down,
           fill_color=COLORS["down"], line_color=COLORS["down"], line_width=0.5)

    # ── Bollinger Bands ──
    bb_data = pd.DataFrame({
        "idx": df["idx"], "upper": df["BB_upper"], "lower": df["BB_lower"],
    }).dropna()
    if not bb_data.empty:
        src_bb = ColumnDataSource(bb_data)
        # Upper band
        ul = p.line("idx", "upper", source=src_bb, color=COLORS["bb_upper"],
                    line_width=1, line_dash="dotted", legend_label="BB Upper")
        ul.level = "underlay"
        # Lower band
        ll = p.line("idx", "lower", source=src_bb, color=COLORS["bb_lower"],
                    line_width=1, line_dash="dotted", legend_label="BB Lower")
        ll.level = "underlay"

    # ── Donchian SL ──
    dc_data = pd.DataFrame({
        "idx": df["idx"], "sl": df["Donchian_lower"],
    }).dropna()
    if not dc_data.empty:
        src_dc = ColumnDataSource(dc_data)
        sl_line = p.line("idx", "sl", source=src_dc, color=COLORS["donchian"],
                         line_width=2, line_dash="dashed", legend_label="SL Donchian (20)")
        sl_line.level = "overlay"

    # ── SMA 20 ──
    sma20_data = pd.DataFrame({"idx": df["idx"], "sma20": df["SMA20"]}).dropna()
    if not sma20_data.empty:
        src_sma20 = ColumnDataSource(sma20_data)
        line = p.line("idx", "sma20", source=src_sma20, color=COLORS["sma20"],
                      line_width=2, legend_label="SMA 20")
        line.level = "overlay"

    # ── SMA 200 ──
    sma200_data = pd.DataFrame({"idx": df["idx"], "sma200": df["SMA200"]}).dropna()
    if not sma200_data.empty:
        src_sma200 = ColumnDataSource(sma200_data)
        line = p.line("idx", "sma200", source=src_sma200, color=COLORS["sma200"],
                      line_width=2, line_dash="dashed", legend_label="SMA 200")
        line.level = "overlay"

    return p


def _adx_figure(p, df):
    """Draw ADX, +DI, -DI indicators on figure p."""
    adx_data = pd.DataFrame({
        "idx": df["idx"], "adx": df["ADX"],
        "pdi": df["+DI"], "mdi": df["-DI"],
    }).dropna()

    if adx_data.empty:
        return p

    src = ColumnDataSource(adx_data)
    p.line("idx", "adx", source=src, color=COLORS["adx"], line_width=2, legend_label="ADX")
    p.line("idx", "pdi", source=src, color=COLORS["pdi"], line_width=1.5,
           line_dash="dashed", legend_label="+DI")
    p.line("idx", "mdi", source=src, color=COLORS["mdi"], line_width=1.5,
           line_dash="dashed", legend_label="-DI")

    for level in [25, 20]:
        span = Span(location=level, dimension="width", line_color=COLORS["ref_line"],
                    line_width=1 if level == 25 else 0.8, line_dash="dotted",
                    line_alpha=0.7 if level == 25 else 0.5)
        p.renderers.append(span)

    p.y_range = Range1d(0, 60)
    p.yaxis.ticker = [0, 10, 20, 25, 30, 40, 50, 60]
    return p


def _format_xaxis(p, df):
    """Format x-axis (integer index) to show date labels."""
    step = max(1, len(df) // 25)
    indices = list(range(0, len(df), step))
    if indices[-1] != len(df) - 1:
        indices.append(len(df) - 1)

    overrides = {}
    for i in indices:
        if isinstance(df.index, pd.DatetimeIndex):
            overrides[i] = df.index[i].strftime("%Y-%m-%d")
        else:
            overrides[i] = str(df.index[i])

    p.xaxis.ticker = FixedTicker(ticks=indices)
    p.xaxis.major_label_overrides = overrides
    p.xaxis.major_label_orientation = 0.785


def generate_chart(ticker, df_plot):
    """
    Generate a full interactive Bokeh chart layout.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol.
    df_plot : pd.DataFrame
        Must contain columns: Open, High, Low, Close, SMA20, SMA200, BB_upper, BB_lower,
        Donchian_lower, ADX, +DI, -DI, Volume with DatetimeIndex.

    Returns
    -------
    tuple
        (script, div) for embedding in Jinja2 template.
    """
    df = df_plot.copy()
    df["idx"] = np.arange(len(df))

    # ── Main price figure ──────────────────────────────────
    p1 = _make_base_figure(
        height=420,
        title=f"{ticker} — Candlestick & Trend Analysis",
        x_range=Range1d(-0.5, len(df) - 0.5),
        sizing_mode="stretch_width",
    )
    p1.yaxis.formatter = NumeralTickFormatter(format="$0,0.00")
    p1.yaxis.minor_tick_line_color = None

    _candlestick_figure(p1, df)
    _format_xaxis(p1, df)
    p1.xaxis.visible = False

    # Crosshair
    p1.add_tools(CrosshairTool(line_color="#666666", line_alpha=0.4))

    # Hover tooltip
    date_strs = [d.strftime("%Y-%m-%d") for d in df.index]
    src_hover = ColumnDataSource(dict(
        idx=df["idx"], Open=df["Open"], High=df["High"],
        Low=df["Low"], Close=df["Close"],
        Volume=df["Volume"] if "Volume" in df.columns else np.zeros(len(df)),
        date_str=date_strs,
    ))

    circ = p1.circle("idx", "Close", source=src_hover, size=1,
                     color=COLORS["bg"], alpha=0.0,
                     hover_color=COLORS["bg"], hover_alpha=0.0)
    circ.level = "underlay"

    hover_tooltips = [
        ("Date", "@date_str"),
        ("Open", "$@{Open}{0,0.00}"),
        ("High", "$@{High}{0,0.00}"),
        ("Low", "$@{Low}{0,0.00}"),
        ("Close", "$@{Close}{0,0.00}"),
        ("Volume", "@{Volume}{0,0}"),
    ]
    hover = HoverTool(tooltips=hover_tooltips, renderers=[circ], toggleable=False)
    p1.add_tools(hover)

    # ── ADX subplot ────────────────────────────────────────
    p2 = _make_base_figure(
        height=160,
        x_range=p1.x_range,
        x_axis_location="below",
        sizing_mode="stretch_width",
    )
    p2.yaxis.formatter = NumeralTickFormatter(format="0.0")
    p2.yaxis.axis_label = "ADX (14)"
    p2.yaxis.axis_label_text_color = COLORS["text"]

    _adx_figure(p2, df)
    _format_xaxis(p2, df)
    p2.xaxis.visible = True
    p2.xaxis.axis_label = ""
    p2.xaxis.major_label_orientation = 0.785

    hover_adx = HoverTool(
        tooltips=[("Date", "$x{%Y-%m-%d}"), ("ADX", "$y{0.0}")],
        formatters={"$x": "datetime"}, mode="mouse", toggleable=False,
    )
    p2.add_tools(hover_adx)

    # Legend styling
    for p in [p1, p2]:
        p.legend.location = "top_left"
        p.legend.label_text_color = COLORS["legend_text"]
        p.legend.label_text_font_size = "10px"
        p.legend.background_fill_color = COLORS["bg"]
        p.legend.background_fill_alpha = 0.8
        p.legend.border_line_color = COLORS["border"]
        p.legend.border_line_alpha = 0.5
        p.legend.click_policy = "hide"

    layout = column(p1, p2, sizing_mode="stretch_width", spacing=0)

    script, div = components(layout)
    return script, div

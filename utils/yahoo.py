import re
from yfinance import Ticker


# Regex for Yahoo Finance ticker validation
TICKER_PATTERN = re.compile(
    r'^[A-Z]{1,5}(\.[A-Z]{2,4})?$'  # e.g. AAPL, MSFT, or with suffix like .US/.ID/.JK
)

SUPPORTED_SUFFIXES = {'US', 'ID', 'JK', 'SE'}


def validate_ticker(ticker):
    """Validate ticker format and test if it exists on Yahoo Finance."""
    if not ticker:
        return False

    # Check basic format
    if not TICKER_PATTERN.match(ticker.strip()):
        return False

    # Try to fetch price — if yfinance can find it, the ticker is valid
    try:
        t = Ticker(ticker)
        hist = t.history(period='1d')
        if len(hist) == 0:
            return False
        return True
    except Exception:
        return False


def fetch_price(ticker):
    """Fetch the latest price for a given ticker from Yahoo Finance.

    Returns float or None on failure. Includes retry with exponential backoff.
    """
    import time

    max_retries = 3
    base_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            t = Ticker(ticker)
            hist = t.history(period='1d')
            if len(hist) == 0:
                return None
            latest = float(hist['Close'].iloc[-1])
            return round(latest, 2)
        except Exception as e:
            wait = base_delay * (2 ** attempt)
            print(f"[Yahoo] Error fetching {ticker} (attempt {attempt+1}/{max_retries}): {e}. Retrying in {wait}s...")
            time.sleep(wait)

    return None


def format_price(price):
    """Format price to 2 decimal places."""
    if price is None:
        return 'N/A'
    return f'{price:.2f}'

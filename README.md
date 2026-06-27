# Portfolio Tracker 📈

A Flask-based web application for tracking stock investment portfolios with real-time pricing from Yahoo Finance, interactive Bokeh charts, and ADX+SMA20 trend analysis.

## Features

- ✅ **Authentication** - Login/Signup with email & password
- ✅ **Multi-user Support** - SQLite database with per-user data isolation
- ✅ **CRUD Portfolio** - Add, Edit, Delete portfolio entries
- ✅ **Real-time Pricing** - Fetch current prices from Yahoo Finance
- ✅ **P&L Calculation** - Calculate profit/loss in both value and percentage
- ✅ **Ticker Validation** - Validate tickers before saving
- ✅ **Refresh Prices** - Update prices individually or all at once
- ✅ **Interactive Chart** - Bokeh candlestick chart with SMA20, SMA200, Bollinger Bands, Donchian SL
- ✅ **ADX Subplot** - ADX(14), +DI, -DI indicators
- ✅ **Trend Analysis** - Multi-window ADX+SMA20 framework (Last 100/200/All bars)
- ✅ **Responsive UI** - Modern design with custom CSS
- ✅ **Docker Support** - Containerized deployment with Docker Compose

## Quick Start (Docker)

```bash
docker compose up -d --build
```

Open http://localhost:5005

## Manual Installation

### Requirements

- Python 3.8+

### Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd portfoliotracker
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
python app.py
```

6. **Open browser**
```
http://localhost:5005
```

## Docker Deployment

### Prerequisites
- Docker & Docker Compose installed

### Build & Run
```bash
# Build image and start container
docker compose up -d --build

# Stop container
docker compose down

# View logs
docker logs portfolio-tracker
```

### Environment Variables (docker-compose.yaml)
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URI` | `sqlite:////app/data/portfolio.db` | SQLite database path (persisted via named volume) |
| `SECRET_KEY` | `portfolio-tracker-docker-secret-key-2024` | Flask secret key |

### Data Persistence
Portfolio data is stored in a Docker named volume `portfolio-data` mounted at `/app/data/`. The data survives container restarts and rebuilds.

## Usage

### 1. Sign Up
- Open the application and click "Sign Up"
- Enter email and password (minimum 6 characters)
- Click "Register"

### 2. Login
- Enter your registered email and password
- Click "Login"

### 3. Add Portfolio Entry
- Click "Add Entry" button
- Enter ticker symbol (example: `BBCA.JK` for Indonesian stocks, `AAPL` for US stocks)
- Enter purchase price
- Enter quantity in shares (not lots)
- Click "Save"
- The app will validate the ticker and fetch current price

### 4. View Portfolio
- View summary: Total Purchase Value, Total Market Value, Total P&L
- View details per entry: Ticker, Purchase Price, Qty, Purchase Value, Current Price, Market Value, P&L Value, P&L %

### 5. Open Chart
- Click any **ticker symbol** (green link) in the table to open the interactive chart page
- Chart includes:
  - Candlestick chart (dark theme)
  - SMA 20 (blue line)
  - SMA 200 (yellow dashed line)
  - Bollinger Bands (grey lines)
  - Donchian Stop Loss (orange dashed line)
  - ADX(14) subplot with +DI/-DI
- Trend analysis panel shows multi-window ADX+SMA20 breakdown

### 6. Refresh Prices
- **Refresh All**: Click "Refresh All" button to update all prices at once
- **Individual**: Click the refresh button on a specific entry

### 7. Edit Entry
- Click "Edit" button on the entry you want to modify
- Update ticker, price, or quantity
- Click "Update"

### 8. Delete Entry
- Click "Delete" button on the entry you want to remove
- Confirm deletion

## Ticker Format

### Indonesian Stocks
- Format: `TICKER.JK`
- Examples: `BBCA.JK`, `TLKM.JK`, `ASII.JK`

### US Stocks
- Format: `TICKER`
- Examples: `AAPL`, `MSFT`, `GOOGL`

### Other Countries
- Check format at [Yahoo Finance](https://finance.yahoo.com)

## Project Structure

```
portfoliotracker/
├── app.py                 # Main Flask application
├── models.py              # Database models (User, PortfolioEntry)
├── auth.py                # Authentication routes
├── views/
│   ├── portfolio.py       # Portfolio CRUD routes
│   └── chart.py           # Bokeh chart page route
├── utils/
│   ├── yahoo.py           # Yahoo Finance utilities
│   ├── indicators.py      # ADX, SMA, BB, Donchian calculations
│   ├── bokeh_chart.py     # Bokeh interactive chart generator
│   └── trend_analysis.py  # ADX+SMA20 trend analysis framework
├── templates/
│   ├── base.html          # Base template with navbar & modal
│   ├── login.html         # Login page
│   ├── signup.html        # Signup page
│   ├── portfolio.html     # Portfolio table page
│   └── chart.html         # Bokeh chart + trend analysis page
├── static/
│   └── favicon.svg        # SVG favicon
├── Dockerfile             # Docker build configuration
├── docker-compose.yaml    # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── .dockerignore          # Docker build context exclusions
└── README.md              # This file
```

## Database Schema

### User
- `id` (Integer, Primary Key)
- `email` (String, Unique)
- `password_hash` (String)

### PortfolioEntry
- `id` (Integer, Primary Key)
- `user_id` (Integer, Foreign Key)
- `ticker` (String) - e.g., "BBCA.JK"
- `purchase_price` (Float) - Purchase price
- `quantity` (Integer) - Number of shares
- `current_price` (Float) - Current price (nullable)

### Calculated Properties

- **Purchase Value**: `quantity × purchase_price`
- **Market Value**: `quantity × current_price`
- **P&L Value**: `market_value - purchase_value`
- **P&L %**: `((market_value - purchase_value) / purchase_value) × 100`

## Notes

- Prices are not streamed real-time; users need to click "Refresh All" or ticker to update
- Ticker validation is performed before saving to ensure ticker is valid on Yahoo Finance
- SQLite database is automatically created when the application runs for the first time
- Passwords are hashed using Werkzeug security
- Session management uses Flask-Login

## Troubleshooting

### Import Error
```bash
pip install -r requirements.txt
```

### Database Error
Delete the `portfolio.db` file (or Docker volume `portfolio-data`) and restart the application to recreate the database.

### Yahoo Finance API Error
Check your internet connection and ensure the ticker format is correct.

## License

MIT License

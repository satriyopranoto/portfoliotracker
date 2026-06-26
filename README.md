# Portfolio Tracker 📈

A Flask-based web application for tracking stock investment portfolios with real-time pricing from Yahoo Finance.

## Features

- ✅ **Authentication** - Login/Signup with email & password
- ✅ **Multi-user Support** - SQLite database with per-user data isolation
- ✅ **CRUD Portfolio** - Add, Edit, Delete portfolio entries
- ✅ **Real-time Pricing** - Fetch current prices from Yahoo Finance
- ✅ **P&L Calculation** - Calculate profit/loss in both value and percentage
- ✅ **Ticker Validation** - Validate tickers before saving
- ✅ **Refresh Prices** - Update prices individually or all at once
- ✅ **Responsive UI** - Modern design with custom CSS

## Requirements

- Python 3.8+
- Flask 3.1.0
- Flask-Login 0.6.3
- Flask-SQLAlchemy 3.1.1
- yfinance 1.4.1
- SQLAlchemy 2.0.37

## Installation

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
pip install flask-sqlalchemy
```

5. **Run the application**
```bash
python app.py
```

6. **Open browser**
```
http://localhost:5005
```

## Usage

### 1. Sign Up
- Open the application and click "Sign Up"
- Enter email and password (minimum 6 characters)
- Click "Daftar" (Register)

### 2. Login
- Enter your registered email and password
- Click "Login"

### 3. Add Portfolio Entry
- Click "Add Entry" button
- Enter ticker symbol (example: `BBCA.JK` for Indonesian stocks, `AAPL` for US stocks)
- Enter purchase price in Rupiah
- Enter quantity in shares (not lots)
- Click "Simpan" (Save)
- The app will validate the ticker and fetch current price

### 4. View Portfolio
- View summary: Total Purchase Value, Total Market Value, Total P&L
- View details per entry: Ticker, Purchase Price, Qty, Purchase Value, Current Price, Market Value, P&L Value, P&L %

### 5. Refresh Prices
- **Refresh All**: Click "Refresh All" button to update all prices at once
- **Individual**: Edit entry to refresh individual price

### 6. Edit Entry
- Click "Edit" button on the entry you want to modify
- Update ticker, price, or quantity
- Click "Update"

### 7. Delete Entry
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
│   └── portfolio.py       # Portfolio CRUD routes
├── utils/
│   └── yahoo.py           # Yahoo Finance utilities
├── templates/
│   ├── base.html          # Base template
│   ├── login.html         # Login page
│   ├── signup.html        # Signup page
│   └── portfolio.html     # Portfolio page
├── requirements.txt       # Python dependencies
├── requirement.txt        # Original requirements document
└── README.md             # This file
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
- `purchase_price` (Float) - Purchase price in Rupiah
- `quantity` (Integer) - Number of shares
- `current_price` (Float) - Current price (nullable)

## Calculated Properties

- **Purchase Value**: `quantity × purchase_price`
- **Market Value**: `quantity × current_price`
- **P&L Value**: `market_value - purchase_value`
- **P&L %**: `((market_value - purchase_value) / purchase_value) × 100`

## Notes

- Prices are not streamed real-time; users need to click "Refresh All" to update
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
Delete the `portfolio.db` file and restart the application to recreate the database.

### Yahoo Finance API Error
Check your internet connection and ensure the ticker format is correct.

## License

MIT License

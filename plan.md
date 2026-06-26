# Portfolio Tracker - Implementation Plan

## ✅ Yang Sudah Ada:

### 1. **Models** (`models.py`)
- `User` model dengan email & password_hash
- `PortfolioEntry` model dengan ticker, purchase_price, quantity, current_price
- Property untuk menghitung purchase_value, market_value, unrealized_pnl_value, unrealized_pnl_pct

### 2. **Authentication** (`auth.py`)
- Signup dengan email & password
- Login dengan validasi
- Logout
- Menggunakan flask-login

### 3. **Portfolio Views** (`views/portfolio.py`)
- CRUD lengkap (index, add, edit, delete)
- Validasi ticker menggunakan Yahoo Finance
- Auto-fetch harga saat page load dan saat add/edit
- Refresh individual entry

### 4. **Yahoo Finance Utils** (`utils/yahoo.py`)
- Validasi ticker format dan ketersediaan
- Fetch harga dengan retry mechanism
- Format price helper

### 5. **Templates** (`templates/base.html`)
- Navbar dengan auth state
- Styling lengkap
- Modal untuk dialog

### 6. **Dependencies** (`requirements.txt`)
- Flask, Flask-Login, SQLAlchemy, yfinance, dll

---

## ✅ Yang Sudah Dilengkapi:

1. **File `app.py`** (main application) - ✅ SELESAI
2. **Template `portfolio.html`** - ✅ SELESAI
3. **Template untuk signup/login** (`login.html`, `signup.html`) - ✅ SELESAI
4. **Database initialization** - ✅ SELESAI (terintegrasi di app.py)
5. **Refresh ALL button** - ✅ SELESAI (route `/portfolio/refresh-all`)
6. **README.md** - ✅ SELESAI (dokumentasi lengkap)
7. **UserMixin** untuk Flask-Login - ✅ SELESAI

---

## 📋 Yang Sudah Dikerjakan:

### 1. **Buat `app.py`** (main Flask application)
- Setup Flask app dengan config
- Register blueprints (auth_bp, portfolio_bp)
- Setup Flask-Login
- Initialize database
- User loader untuk Flask-Login

### 2. **Buat template `portfolio.html`**
- Tabel portfolio dengan kolom:
  - Ticker
  - Purchase Price
  - Qty
  - Purchase Value
  - Current Price
  - Market Value
  - P&L Value
  - P&L %
- Tombol CRUD di atas tabel (Add, Edit, Delete)
- Tombol Refresh All untuk refresh semua harga sekaligus
- Integrate dengan modal dari base.html

### 3. **Buat halaman login/signup** atau update base.html
- Form login dengan email & password
- Form signup dengan email & password
- Flash messages untuk error/success

### 4. **Tambahkan route refresh_all**
- Loop semua entries milik user
- Fetch harga terbaru untuk semua ticker
- Update database

### 5. **Testing & Verification**
- Jalankan aplikasi
- Test signup, login, logout
- Test CRUD portfolio
- Test validasi ticker
- Test refresh price (individual & all)

---

## 🎯 Requirements dari User:

- ✅ Flask Python web application
- ✅ Login/Authentication dengan email & password
- ✅ Signup feature
- ✅ Entry ticker asset (format Yahoo Finance, contoh: saham Indonesia dengan suffix .JK)
- ✅ Input harga pembelian & qty dalam satuan share/lembar (bukan lot)
- ✅ Portfolio disimpan dalam SQLite dengan multi-user support (key: email/user_id)
- ✅ Harga terkini diambil dari Yahoo Finance
- ✅ Perhitungan P&L dalam percent dan value
- ✅ Hitung purchase value (qty × harga pembelian)
- ✅ Hitung market value (qty × harga terkini)
- ✅ Auto-fetch harga saat page load dan new entry
- ✅ Tombol refresh untuk update harga (tidak streaming/monitoring terus-menerus)
- ✅ CRUD buttons (Add/New, Modify, Delete)
- ✅ Dialog untuk input ticker, harga pembelian, qty
- ✅ Validasi ticker di Yahoo Finance sebelum save
- ❌ Refresh ALL belum ada (hanya refresh per-entry)

---

## 📝 Notes:

- Database: SQLite dengan SQLAlchemy ORM
- Authentication: Flask-Login
- Price source: yfinance library
- UI: Custom CSS (no external framework)
- Bahasa: Indonesia (UI & messages)

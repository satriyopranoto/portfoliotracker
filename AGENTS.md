# Portfolio Tracker - Agent Reference

## Common Issues & Fixes

---

### 1. Database Hilang Setelah Rebuild Docker

**Symptom:** Setelah `docker build` + `docker run`, data user dan portfolio hilang. Tidak bisa login.

**Root cause:** Dua masalah:
1. **Volume mount tidak dipakai** — `docker run` tanpa `-v portfolio-data:/app/data` membuat container memakai database baru di layer writable container.
2. **Environment variable `DATABASE_URI` tidak diset** — Default Flask `sqlite:///portfolio.db` mengarah ke `/app/instance/portfolio.db`, BUKAN ke `/app/data/portfolio.db` yang ada volumenya.

**Fix:** Saat `docker run`, pastikan dua hal ini:
- Mount volume: `-v portfoliotracker_portfolio-data:/app/data`
- Set env: `-e DATABASE_URI=sqlite:////app/data/portfolio.db`

**Deploy command yang benar:**
```bash
docker run -d --name portfolio-tracker --restart unless-stopped \
  -p 5005:5005 \
  -v portfoliotracker_portfolio-data:/app/data \
  -e DATABASE_URI=sqlite:////app/data/portfolio.db \
  -e SECRET_KEY=portfolio-tracker-docker-secret-key-2024 \
  portfoliotracker-portfolio-tracker:latest
```

Atau lebih gampang: `docker compose up -d --build` — compose otomatis handle volume + env.

**Reset password via shell:**
```bash
docker exec portfolio-tracker python3 -c "
from werkzeug.security import generate_password_hash
import sqlite3
conn = sqlite3.connect('/app/data/portfolio.db')
cur = conn.cursor()
pw_hash = generate_password_hash('newpassword')
cur.execute('UPDATE users SET password_hash = ? WHERE email = ?', (pw_hash, 'user@email.com'))
conn.commit()
conn.close()
print('Password reset done!')
"
```

**Key locations:**
- `docker-compose.yaml` — volume `portfolio-data:/app/data` + env `DATABASE_URI`
- `app.py` line 15 — fallback `sqlite:///portfolio.db` (instance folder)
- `auth.py` — `check_password_hash()` dan `generate_password_hash()` menggunakan scrypt

---

### 2. Timeframe Selector (H1/H4/D1/W1/MN)

**Feature:** Chart page mendukung switching timeframe — tombol H1, H4, D1 (default), W1, MN di bawah chart.

**Bagaimana cara kerjanya:**
- Backend (`views/chart.py`) membaca query param `?tf=1h|4h|1d|1wk|1mo`
- Data di-download dari Yahoo Finance dengan period/interval sesuai:
  | Tombol | Interval | Period | Notes |
  |--------|----------|--------|-------|
  | H1 | 1h | 30d | Data 1 jam |
  | H4 | 1h di-resample ke 4h | 60d | OHLC resample |
  | D1 | 1d | 2y | Default |
  | W1 | 1wk | 5y | Weekly |
  | MN | 1mo | 10y | Monthly |
- Semua indikator (ADX, SMA, BB, Donchian, Trend Analysis) otomatis kalkulasi ulang berdasarkan timeframe yang dipilih
- Tombol aktif punya highlight gold (`#d4af37`)

**Key locations:**
- `views/chart.py` — `TIMEFRAMES` dict, `_fetch_data()`, `chart_view()` route
- `templates/chart.html` — Timeframe selector buttons di bawah chart div

**Flow:**
1. User klik tombol timeframe → `url_for('chart.chart_view', ticker=X, tf=X)` → reload halaman
2. Backend fetch data sesuai timeframe
3. Backend kalkulasi ulang semua indikator
4. Bokeh chart di-render ulang dengan data baru
5. Trend analysis stats ikut update sesuai timeframe

**Peringatan:**
- Data 1h/4h butuh koneksi internet stabil karena jumlah bar lebih banyak
- Resample 4h dari data 1h — minimal 30 bar setelah resample, jika kurang pakai data 1h original

---

### 3. Stop Loss (SL) — Direction-Dependent Donchian (Fix)

**Symptom (sebelum fix):** SL menggunakan simple Donchian Channel `period=20` — hanya lower channel sebagai SL. Tidak direction-dependent. Tidak match dengan EA MT4 dan stocktrade.

**Fix:** Ganti `calculate_donchian()` dengan `calculate_sl()` dari `utils/indicators.py`.

**Logic `calculate_sl()` (sama persis dengan stocktrade & EA MT4):**

```python
ero = atr_multiple * atr_period        # default: 2.8 x 10 = 28
r_prev = high.rolling(ero).max().shift(1)  # Highest high (shift 1)
s_prev = low.rolling(ero).min().shift(1)   # Lowest low (shift 1)
r_curr = high.rolling(ero).max()
s_curr = low.rolling(ero).min()

ab = high > r_prev ? 1 : (low < s_prev ? -1 : 0)  # Trigger arah
ac = ffill(ab)                                      # Persist direction
sl = ac == 1 ? s_curr : r_curr                      # SL sesuai arah
```

**Perbedaan dengan Donchian biasa:**

| Aspek | Donchian biasa (old) | `calculate_sl()` (new) |
|-------|---------------------|------------------------|
| Lookback | 20 bar | 28 bar (2.8 × 10) |
| Direction | Tidak, SL tetap lower | Ya — uptrend: lower channel, downtrend: upper channel |
| Shift 1 | Tidak (look-ahead bias) | Ya — pake `.shift(1)` untuk r_prev/s_prev |
| Ffill | Tidak | Ya — directional persistence |

**Key locations:**
- `utils/indicators.py` — `calculate_sl()` function
- `views/chart.py` line ~100 — panggil `calculate_sl(df, atr_multiple=2.8, atr_period=10)`
- `utils/bokeh_chart.py` — membaca `df['Donchian_lower']` untuk plotting (column name tetap sama)

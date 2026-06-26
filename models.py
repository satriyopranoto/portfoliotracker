from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    portfolio_entries = db.relationship('PortfolioEntry', backref='user', lazy=True)


class PortfolioEntry(db.Model):
    __tablename__ = 'portfolio_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticker = db.Column(db.String(20), nullable=False)  # e.g. "BBCA.JK"
    purchase_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # satuan lembar/share

    current_price = db.Column(db.Float, nullable=True)  # diisi saat fetch

    @property
    def purchase_value(self):
        return round(self.quantity * self.purchase_price, 2)

    @property
    def market_value(self):
        if self.current_price:
            return round(self.quantity * self.current_price, 2)
        return None

    @property
    def unrealized_pnl_value(self):
        pv = self.purchase_value
        mv = self.market_value
        if pv and mv is not None:
            return round(mv - pv, 2)
        return None

    @property
    def unrealized_pnl_pct(self):
        pv = self.purchase_value
        mv = self.market_value
        if pv and mv is not None and pv > 0:
            return round(((mv - pv) / pv) * 100, 2)
        return None

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, PortfolioEntry
from utils.yahoo import fetch_price, validate_ticker


portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/')
@login_required
def index():
    entries = PortfolioEntry.query.filter_by(user_id=current_user.id).all()

    # Auto-fetch latest prices and calculate P&L for each entry
    for entry in entries:
        if not entry.current_price or entry.current_price == 0:
            price = fetch_price(entry.ticker)
            if price is not None:
                entry.current_price = price

    return render_template('portfolio.html', entries=entries, user=current_user)


@portfolio_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        ticker = request.form.get('ticker', '').strip()
        purchase_price_str = request.form.get('purchase_price', '')
        quantity_str = request.form.get('quantity', '')

        # Validate fields
        if not ticker or not purchase_price_str or not quantity_str:
            flash('All fields are required.', 'error')
            return redirect(url_for('portfolio.add'))

        try:
            purchase_price = float(purchase_price_str)
            quantity = int(quantity_str)
        except (ValueError, TypeError):
            flash('Price and quantity must be numbers.', 'error')
            return redirect(url_for('portfolio.add'))

        if purchase_price <= 0 or quantity <= 0:
            flash('Price and quantity must be greater than 0.', 'error')
            return redirect(url_for('portfolio.add'))

        # Validate ticker
        if not validate_ticker(ticker):
            flash(f'Ticker "{ticker}" is invalid or not found on Yahoo Finance.', 'error')
            return redirect(url_for('portfolio.add'))

        entry = PortfolioEntry(
            user_id=current_user.id,
            ticker=ticker.upper(),
            purchase_price=purchase_price,
            quantity=quantity
        )
        db.session.add(entry)

        # Fetch current price and calculate P&L immediately
        price = fetch_price(ticker.upper())
        if price is not None:
            entry.current_price = price

        db.session.commit()
        flash(f'Entry "{ticker}" added successfully!', 'success')
        return redirect(url_for('portfolio.index'))

    return render_template('portfolio.html', entries=[], user=current_user, show_add_form=True)


@portfolio_bp.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit(entry_id):
    entry = PortfolioEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        ticker = request.form.get('ticker', '').strip()
        purchase_price_str = request.form.get('purchase_price', '')
        quantity_str = request.form.get('quantity', '')

        try:
            purchase_price = float(purchase_price_str)
            quantity = int(quantity_str)
        except (ValueError, TypeError):
            flash('Price and quantity must be numbers.', 'error')
            return redirect(url_for('portfolio.edit', entry_id=entry.id))

        if purchase_price <= 0 or quantity <= 0:
            flash('Price and quantity must be greater than 0.', 'error')
            return redirect(url_for('portfolio.edit', entry_id=entry.id))

        # Validate ticker
        if not validate_ticker(ticker):
            flash(f'Ticker "{ticker}" is invalid or not found on Yahoo Finance.', 'error')
            return redirect(url_for('portfolio.edit', entry_id=entry.id))

        entry.ticker = ticker.upper()
        entry.purchase_price = purchase_price
        entry.quantity = quantity

        # Fetch current price and recalculate P&L
        price = fetch_price(ticker.upper())
        if price is not None:
            entry.current_price = price

        db.session.commit()
        flash(f'Entry "{ticker}" updated successfully!', 'success')
        return redirect(url_for('portfolio.index'))

    return render_template('portfolio.html', entries=[entry], user=current_user, show_edit_form=True, edit_entry=entry)


@portfolio_bp.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete(entry_id):
    entry = PortfolioEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    ticker = entry.ticker

    db.session.delete(entry)
    db.session.commit()
    flash(f'Entry "{ticker}" deleted successfully.', 'success')
    return redirect(url_for('portfolio.index'))


@portfolio_bp.route('/refresh/<int:entry_id>', methods=['POST'])
@login_required
def refresh_price(entry_id):
    entry = PortfolioEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()

    price = fetch_price(entry.ticker)
    if price is not None:
        entry.current_price = price
        db.session.commit()
        flash(f'Price for "{entry.ticker}" refreshed successfully!', 'success')
    else:
        flash(f'Failed to fetch price for "{entry.ticker}".', 'error')

    return redirect(url_for('portfolio.index'))


@portfolio_bp.route('/refresh-all')
@login_required
def refresh_all():
    """Refresh all portfolio entries for the current user."""
    entries = PortfolioEntry.query.filter_by(user_id=current_user.id).all()
    
    if not entries:
        flash('Your portfolio is empty.', 'warning')
        return redirect(url_for('portfolio.index'))
    
    success_count = 0
    failed_tickers = []
    
    for entry in entries:
        price = fetch_price(entry.ticker)
        if price is not None:
            entry.current_price = price
            success_count += 1
        else:
            failed_tickers.append(entry.ticker)
    
    db.session.commit()
    
    if success_count > 0:
        flash(f'Successfully refreshed {success_count} prices.', 'success')
    
    if failed_tickers:
        flash(f'Failed to fetch prices for: {", ".join(failed_tickers)}', 'error')
    
    return redirect(url_for('portfolio.index'))

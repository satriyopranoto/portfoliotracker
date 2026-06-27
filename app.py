from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from models import db, User
from auth import auth_bp
from views.portfolio import portfolio_bp
from views.chart import chart_bp
import os


def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///portfolio.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(portfolio_bp, url_prefix='/portfolio')
    app.register_blueprint(chart_bp, url_prefix='')
    
    # Root route - redirect to portfolio or login
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('portfolio.index'))
        return redirect(url_for('auth.login'))
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5005)

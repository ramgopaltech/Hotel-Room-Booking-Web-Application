import os
from flask import Flask, render_template
from config import Config
from models import db
from utils import seed_initial_data
from routes import main_bp, auth_bp, booking_bp, admin_bp, api_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # Custom Jinja filters
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    # Context processors
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}

    # Initialize database & seed initial data within app context
    with app.app_context():
        db.create_all()
        seed_initial_data()

    return app

app = create_app()

if __name__ == '__main__':
    print("Starting Grand Royale Luxury Hotel Application on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

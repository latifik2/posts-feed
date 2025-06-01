from flask_sqlalchemy import SQLAlchemy
from utils.config import get_config

db = SQLAlchemy()  # Инициализация SQLAlchemy

def init_db(app):
    """Инициализирует подключение к БД"""
    config = get_config()
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app)
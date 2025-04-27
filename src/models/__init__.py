from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Инициализация SQLAlchemy
def init_db(app):
    """Инициализирует подключение к БД"""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Пример для SQLite
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
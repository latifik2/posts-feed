import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, flash, url_for
from dotenv import load_dotenv
import psycopg2
from pymongo import MongoClient
import redis
import bcrypt
from utils.config import get_config
from database.users import UserService
from utils.validators import validate_user_data, validate_login_data, validate_post_data

# Load environment variables from .env file
load_dotenv()

# Get the current configuration
config = get_config()

app = Flask(__name__)
app.config.from_object(config)

# PostgreSQL setup (Users)
#pg_conn = psycopg2.connect(app.config['DATABASE_URL'])

# MongoDB setup (Posts)
#mongo_client = MongoClient(app.config['MONGO_URI'])
#mongo_db = mongo_client[app.config['MONGO_DB']]
#posts_collection = mongo_db.posts

# Redis setup (Cache)
#redis_client = redis.Redis(
#    host=app.config['REDIS_HOST'],
#    port=app.config['REDIS_PORT'],
#    db=0
#)

# Инициализация сервиса пользователей
user_service = UserService()

@app.route('/')
def feed():
    # Mock response for feed
    mock_posts = [
        {
            '_id': '1',
            'user_id': 1,
            'username': 'demo_user',
            'content': 'Это демо пост',
            'created_at': datetime.now()
        }
    ]
    return render_template('feed.html', posts=mock_posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        is_valid, error_message = validate_user_data(username, email, password, first_name, last_name)
        if not is_valid:
            flash(error_message)
            return render_template('register.html')
            
        try:
            # Проверяем, существует ли пользователь с таким именем или email
            if user_service.get_user_by_username(username):
                return "Ошибка: Пользователь с таким именем уже существует", 400
                
            if user_service.get_user_by_email(email):
                return "Ошибка: Пользователь с таким email уже существует", 400
            
            # Создаем нового пользователя
            user = user_service.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name if first_name else None,
                last_name=last_name if last_name else None
            )
            
            # Автоматически входим пользователя после регистрации
            session['user_id'] = user.id
            
            flash('Регистрация успешна!')
            return redirect(url_for('login'))
            
        except Exception as e:
            # В реальном приложении здесь нужно логировать ошибку
            return f"Ошибка при регистрации: {str(e)}", 500
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        is_valid, error_message = validate_login_data(username, password)
        if not is_valid:
            flash(error_message)
            return render_template('login.html')
            
        try:
            # Получаем пользователя по имени
            user = user_service.get_user_by_username(username)
            
            # Проверяем, существует ли пользователь и правильный ли пароль
            if not user or not user_service.check_password(user, password):
                return "Ошибка: Неверное имя пользователя или пароль", 400
            
            # Устанавливаем сессию
            session['user_id'] = user.id
            flash('Вход выполнен успешно!')
            return redirect(url_for('feed'))
               
        except Exception as e:
            # В реальном приложении здесь нужно логировать ошибку
            return f"Ошибка при входе: {str(e)}", 500

@app.route('/post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        flash('Необходимо войти в систему')
        return redirect(url_for('login'))
        
    content = request.form.get('content', '').strip()
    
    is_valid, error_message = validate_post_data(content)
    if not is_valid:
        flash(error_message)
        return redirect(url_for('feed'))
        
    # Здесь будет код для сохранения поста в базу данных
    flash('Пост успешно создан!')
    return redirect(url_for('feed'))

@app.route('/post/<post_id>', methods=['PUT', 'DELETE'])
def manage_post(post_id):
    if 'user_id' not in session:
        flash('Необходимо войти в систему')
        return redirect(url_for('login'))
        
    if request.method == 'PUT':
        content = request.form.get('content', '').strip()
        
        is_valid, error_message = validate_post_data(content)
        if not is_valid:
            flash(error_message)
            return redirect(url_for('feed'))
            
        # Здесь будет код для обновления поста
        flash('Пост успешно обновлен!')
    elif request.method == 'DELETE':
        # Здесь будет код для удаления поста
        flash('Пост успешно удален!')
        
    return redirect(url_for('feed'))

def get_username(user_id):
    # Mock username retrieval
    # with pg_conn.cursor() as cur:
    #     cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    #     return cur.fetchone()[0]
    return "mock_user"

if __name__ == '__main__':
    app.run()
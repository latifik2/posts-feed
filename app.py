import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, flash
from dotenv import load_dotenv
import psycopg2
from pymongo import MongoClient
import redis
import bcrypt
from utils.config import get_config
from database.users import UserService

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

def get_cached_posts():
    # cached = redis_client.get('last_posts')
    # return eval(cached.decode()) if cached else None
    pass

def cache_posts(posts):
    # redis_client.setex('last_posts', 300, str(posts[:5]))
    pass

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
        # Получаем данные из формы
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        # Проверка обязательных полей
        if not username:
            return "Ошибка: Имя пользователя обязательно", 400
        if not email:
            return "Ошибка: Email обязателен", 400
        if not password:
            return "Ошибка: Пароль обязателен", 400
            
        # Проверка длины имени пользователя
        if len(username) < 3:
            return "Ошибка: Имя пользователя должно содержать минимум 3 символа", 400
        if len(username) > 64:
            return "Ошибка: Имя пользователя не должно превышать 64 символа", 400
            
        # Проверка длины пароля
        if len(password) < 6:
            return "Ошибка: Пароль должен содержать минимум 6 символов", 400
            
        # Проверка валидности email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return "Ошибка: Некорректный формат email", 400
            
        # Проверка длины имени и фамилии (если они указаны)
        if first_name and len(first_name) > 64:
            return "Ошибка: Имя не должно превышать 64 символа", 400
        if last_name and len(last_name) > 64:
            return "Ошибка: Фамилия не должна превышать 64 символа", 400
            
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
            
            return redirect('/')
            
        except Exception as e:
            # В реальном приложении здесь нужно логировать ошибку
            return f"Ошибка при регистрации: {str(e)}", 500
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    # Получаем данные из формы и удаляем лишние пробелы
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    # Проверка обязательных полей
    if not username:
        return "Ошибка: Имя пользователя обязательно", 400
    if not password:
        return "Ошибка: Пароль обязателен", 400
    
    try:
        # Получаем пользователя по имени
        user = user_service.get_user_by_username(username)
        
        # Проверяем, существует ли пользователь и правильный ли пароль
        if not user or not user_service.check_password(user, password):
            return "Ошибка: Неверное имя пользователя или пароль", 400
        
        # Устанавливаем сессию
        session['user_id'] = user.id
        return redirect('/')
        
    except Exception as e:
        # В реальном приложении здесь нужно логировать ошибку
        return f"Ошибка при входе: {str(e)}", 500

@app.route('/post', methods=['POST'])
def create_post():
    content = request.form['content']
    
    # Validation
    if not content:
        return "Ошибка: Содержание поста не может быть пустым", 400
    if len(content) > 1000:
        return "Ошибка: Пост слишком длинный (максимум 1000 символов)", 400
    
    # Mock post creation
    # post = {
    #     'user_id': session['user_id'],
    #     'username': get_username(session['user_id']),
    #     'content': content,
    #     'created_at': datetime.now()
    # }
    # posts_collection.insert_one(post)
    # redis_client.delete('last_posts')
    
    return "Запрос выполнен успешно", 200

@app.route('/post/<post_id>', methods=['PUT', 'DELETE'])
def manage_post(post_id):
    if request.method == 'PUT':
        content = request.form.get('content')
        
        # Validation
        if not content:
            return "Ошибка: Содержание поста не может быть пустым", 400
        if len(content) > 1000:
            return "Ошибка: Пост слишком длинный (максимум 1000 символов)", 400
        
        # Mock post update
        # posts_collection.update_one(
        #     {'_id': post_id},
        #     {'$set': {'content': content}}
        # )
        # redis_client.delete('last_posts')
        return "Контент изменен успешно", 200
    
    elif request.method == 'DELETE':
        # Mock post deletion
        # posts_collection.delete_one({'_id': post_id})
        # redis_client.delete('last_posts')
        return "Пост удален успешно", 200

def get_username(user_id):
    # Mock username retrieval
    # with pg_conn.cursor() as cur:
    #     cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    #     return cur.fetchone()[0]
    return "mock_user"

if __name__ == '__main__':
    app.run()
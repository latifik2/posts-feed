import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
import psycopg2
from pymongo import MongoClient
import redis
import bcrypt
from utils.config import get_config

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
        username = request.form['username']
        password = request.form['password']
        
        # Validation
        if not username or not password:
            return "Ошибка: Имя пользователя и пароль обязательны", 400
        if len(username) < 3:
            return "Ошибка: Имя пользователя должно содержать минимум 3 символа", 400
        if len(password) < 6:
            return "Ошибка: Пароль должен содержать минимум 6 символов", 400
            
        # Mock successful registration
        # with pg_conn.cursor() as cur:
        #     cur.execute(
        #         "INSERT INTO users (username, password) VALUES (%s, %s)",
        #         (username, password)
        #     )
        #     pg_conn.commit()
        return "Регистрация успешно выполнена", 200
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    username = request.form['username']
    password = request.form['password']
    
    # Validation
    if not username or not password:
        return "Ошибка: Имя пользователя и пароль обязательны", 400
        
    # Mock successful login
    # with pg_conn.cursor() as cur:
    #     cur.execute(
    #         "SELECT id, password FROM users WHERE username = %s",
    #         (username,)
    #     )
    #     user = cur.fetchone()
    #     
    #     if user and bcrypt.checkpw(password, user[1]):
    #         session['user_id'] = user[0]
    
    session['user_id'] = 1  # Mock user ID
    return redirect('/')

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
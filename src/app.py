# flake8: noqa

from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for,
    jsonify
)
from dotenv import load_dotenv
import redis
import json
import logging
from utils.config import get_config
from database.users import UserService
from utils.validators import (
    validate_user_data,
    validate_login_data,
    validate_post_data
)
from models.post import Post
from database.repositories import PostRepository

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the current configuration
config = get_config()

app = Flask(__name__)
app.config.from_object(config)

# Настройка логирования Flask
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Инициализация сервиса пользователей
user_service = UserService()

# Add post_repository instance after user_service initialization
post_repository = PostRepository()

# Инициализация Redis
redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=0,
    decode_responses=True
)

# Ключ для кеша последних постов
RECENT_POSTS_CACHE_KEY = 'recent_posts'
# Время жизни кеша (в секундах)
CACHE_TTL = 300  # 5 минут

def get_cached_posts():
    """Получить последние посты из кеша Redis"""
    cached_data = redis_client.get(RECENT_POSTS_CACHE_KEY)
    if cached_data:
        return json.loads(cached_data)
    return None

def cache_posts(posts):
    """Сохранить посты в кеш Redis"""
    posts_data = []
    for post in posts:
        post_dict = {
            'id': str(post.id),
            'content': post.content,
            'created_at': post.created_at.isoformat(),
            'username': get_username(post.author_id)
        }
        posts_data.append(post_dict)
    
    redis_client.setex(
        RECENT_POSTS_CACHE_KEY,
        CACHE_TTL,
        json.dumps(posts_data)
    )
    return posts_data

@app.route('/')
def feed():
    # Пытаемся получить посты из кеша
    cached_posts = get_cached_posts()
    
    if cached_posts:
        # Если посты есть в кеше, используем их
        # Преобразуем строки дат в объекты datetime
        for post in cached_posts:
            post['created_at'] = datetime.fromisoformat(post['created_at'])
        posts = cached_posts
    else:
        # Если постов нет в кеше, получаем их из MongoDB и кешируем
        mongo_posts = post_repository.get_posts(limit=10)
        # Преобразуем посты в словари для шаблона
        posts = []
        for post in mongo_posts:
            username = get_username(post.author_id)
            print(f"Debug - Post author_id: {post.author_id}, username: {username}")  # Debug line
            post_dict = {
                'id': str(post.id),
                'content': post.content,
                'created_at': post.created_at,
                'username': username
            }
            posts.append(post_dict)
        # Кешируем посты
        cache_posts(mongo_posts)
    
    return render_template('feed.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        app.logger.debug("Starting registration process...")
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        app.logger.debug(f"Received registration data - username: {username}, email: {email}")
        
        is_valid, error_message = validate_user_data(username, email, password, first_name, last_name)
        if not is_valid:
            app.logger.debug(f"Validation failed - {error_message}")
            flash(error_message)
            return render_template('register.html')
            
        try:
            # Проверяем, существует ли пользователь с таким именем или email
            existing_user = user_service.get_user_by_username(username)
            if existing_user:
                app.logger.debug(f"Username {username} already exists")
                flash("Ошибка: Пользователь с таким именем уже существует")
                return render_template('register.html')
                
            existing_email = user_service.get_user_by_email(email)
            if existing_email:
                app.logger.debug(f"Email {email} already exists")
                flash("Ошибка: Пользователь с таким email уже существует")
                return render_template('register.html')
            
            app.logger.debug("Creating new user...")
            # Создаем нового пользователя
            user = user_service.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name if first_name else None,
                last_name=last_name if last_name else None
            )
            
            if user and user.id:
                app.logger.debug(f"User created successfully with ID: {user.id}")
                # Автоматически входим пользователя после регистрации
                session['user_id'] = user.id
                flash('Регистрация успешна!')
                return redirect(url_for('login'))
            else:
                app.logger.error("User creation failed - no user ID returned")
                flash("Ошибка при создании пользователя")
                return render_template('register.html')
            
        except Exception as e:
            app.logger.error(f"Error during registration: {str(e)}", exc_info=True)
            flash(f"Ошибка при регистрации: {str(e)}")
            return render_template('register.html')
            
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
        
    user_id = session['user_id']
    post = Post(
        title="",  # или request.form.get('title', '').strip()
        content=content,
        author_id=user_id
    )

    try:
        created_post = post_repository.create_post(post)
        
        # Обновляем кеш после создания нового поста
        redis_client.delete(RECENT_POSTS_CACHE_KEY)
        
        flash('Пост успешно создан!')
    except Exception as e:
        flash(f'Ошибка при создании поста: {str(e)}')
    return redirect(url_for('feed'))

@app.route('/post/<post_id>', methods=['PUT', 'DELETE'])
def manage_post(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Необходимо войти в систему'}), 401
        
    if request.method == 'PUT':
        data = request.get_json()
        content = data.get('content', '').strip()
        
        is_valid, error_message = validate_post_data(content)
        if not is_valid:
            return jsonify({'error': error_message}), 400
            
        post = post_repository.get_post(post_id)
        if post and post.author_id == session['user_id']:
            post.content = content
            post_repository.update_post(post_id, post)
            
            # Обновляем кеш после редактирования поста
            redis_client.delete(RECENT_POSTS_CACHE_KEY)
            
            return jsonify({'message': 'Пост успешно обновлен!'}), 200
        else:
            return jsonify({'error': 'Пост не найден или у вас нет прав на его редактирование'}), 403
            
    elif request.method == 'DELETE':
        post = post_repository.get_post(post_id)
        if post and post.author_id == session['user_id']:
            post_repository.delete_post(post_id)
            
            # Обновляем кеш после удаления поста
            redis_client.delete(RECENT_POSTS_CACHE_KEY)
            
            return jsonify({'message': 'Пост успешно удален!'}), 200
        else:
            return jsonify({'error': 'Пост не найден или у вас нет прав на его удаление'}), 403

@app.route('/profile', methods=['GET', 'POST', 'DELETE'])
def profile():
    if 'user_id' not in session:
        flash('Необходимо войти в систему')
        return redirect(url_for('login'))

    # Получаем данные пользователя
    user = user_service.get_user_by_id(session['user_id'])
    if not user:
        flash('Пользователь не найден')
        return redirect(url_for('login'))

    # Обработка DELETE запроса (удаление профиля)
    if request.method == 'DELETE' or (request.method == 'POST' and request.form.get('_method') == 'DELETE'):
        # Проверяем пароль для подтверждения
        confirm_password = request.form.get('confirm_password', '').strip()
        if not user_service.check_password(user, confirm_password):
            flash('Неверный пароль')
            return redirect(url_for('profile'))
        
        # Удаляем пользователя
        try:
            if user_service.delete_user(user):
                # Очищаем сессию
                session.clear()
                flash('Профиль успешно удален')
                return redirect(url_for('login'))
            else:
                flash('Ошибка при удалении профиля')
                return redirect(url_for('profile'))
        except Exception as e:
            flash(f'Ошибка при удалении профиля: {str(e)}')
            return redirect(url_for('profile'))
    
    # Обработка POST запроса (обновление профиля)
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        current_password = request.form.get('current_password', '').strip()
        
        # Проверяем текущий пароль
        if not user_service.check_password(user, current_password):
            flash('Неверный пароль')
            return render_template('profile.html', user=user)
        
        # Проверяем email
        if email != user.email:
            # Проверяем, не занят ли email другим пользователем
            existing_user = user_service.get_user_by_email(email)
            if existing_user and existing_user.id != user.id:
                flash('Email уже используется другим пользователем')
                return render_template('profile.html', user=user)
        
        # Обновляем данные пользователя
        try:
            user_service.update_user(
                user_id=user.id,
                email=email,
                first_name=first_name if first_name else None,
                last_name=last_name if last_name else None
            )
            flash('Профиль успешно обновлен')
            return redirect(url_for('profile'))
        except Exception as e:
            flash(f'Ошибка при обновлении профиля: {str(e)}')
    
    # GET запрос - отображение профиля
    return render_template('profile.html', user=user)

@app.route('/load_more')
def load_more():
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 10))
    
    # Всегда загружаем посты из MongoDB для кнопки "Загрузить еще"
    posts = post_repository.get_posts(skip=skip, limit=limit)
    posts_data = []
    
    for post in posts:
        post_dict = {
            'id': str(post.id),
            'content': post.content,
            'created_at': post.created_at.isoformat(),
            'username': get_username(post.author_id)
        }
        posts_data.append(post_dict)
    
    return jsonify({'posts': posts_data})

def get_username(user_id):
    print(f"Debug - Getting username for user_id: {user_id}")  # Debug line
    user = user_service.get_user_by_id(user_id)
    print(f"Debug - Retrieved user: {user}")  # Debug line
    if user:
        return user.username
    return "Неизвестный пользователь"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
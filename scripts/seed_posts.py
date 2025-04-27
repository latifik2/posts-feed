import os
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from bson import ObjectId
from database.repositories import PostRepository
from models.post import Post

def generate_test_posts(count=50):
    post_repository = PostRepository()
    
    # Список возможных авторов (используем ID от 1 до 5)
    author_ids = list(range(1, 6))
    
    # Список возможных тегов
    tags = ['python', 'flask', 'mongodb', 'web', 'development', 'testing', 'database', 'api', 'backend', 'frontend']
    
    # Список возможных заголовков
    titles = [
        'Интересный пост о программировании',
        'Новости веб-разработки',
        'Советы по работе с MongoDB',
        'Изучаем Flask',
        'Python для начинающих',
        'Базы данных в веб-приложениях',
        'API дизайн',
        'Тестирование веб-приложений',
        'Оптимизация производительности',
        'Безопасность веб-приложений'
    ]
    
    # Список возможных содержимых постов
    contents = [
        'Это очень интересный пост о программировании. Здесь много полезной информации.',
        'Сегодня я узнал много нового о веб-разработке. Хочу поделиться с вами.',
        'MongoDB - отличная база данных для веб-приложений. Вот почему.',
        'Flask - это легкий и мощный фреймворк для создания веб-приложений.',
        'Python - отличный язык для начинающих программистов.',
        'Базы данных - важная часть любого веб-приложения. Давайте разберемся, как они работают.',
        'API дизайн - это искусство. Вот несколько советов по созданию хорошего API.',
        'Тестирование - важная часть разработки. Без него не обойтись.',
        'Производительность веб-приложений - это важно. Вот как её улучшить.',
        'Безопасность - важный аспект веб-разработки. Не забывайте об этом.'
    ]
    
    # Генерируем посты
    for i in range(count):
        # Случайный автор
        author_id = random.choice(author_ids)
        
        # Случайный заголовок
        title = random.choice(titles)
        
        # Случайное содержимое
        content = random.choice(contents)
        
        # Случайные теги (от 0 до 3)
        post_tags = random.sample(tags, random.randint(0, 3))
        
        # Случайное количество лайков
        likes = random.randint(0, 100)
        
        # Случайная дата создания (в пределах последних 30 дней)
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        
        # Создаем пост
        post = Post(
            title=title,
            content=content,
            author_id=author_id,
            tags=post_tags,
            likes=likes,
            created_at=created_at,
            updated_at=created_at
        )
        
        # Сохраняем пост в базу данных
        try:
            post_repository.create_post(post)
            print(f"Создан пост {i+1}/{count}")
        except Exception as e:
            print(f"Ошибка при создании поста {i+1}: {str(e)}")

if __name__ == "__main__":
    print("Начинаем создание тестовых постов...")
    generate_test_posts()
    print("Готово! Тестовые посты созданы.") 
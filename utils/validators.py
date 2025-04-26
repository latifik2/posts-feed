import re

def validate_user_data(username, email, password, first_name=None, last_name=None):
    """
    Валидация данных пользователя при регистрации.
    Возвращает кортеж (is_valid, error_message).
    """
    # Проверка обязательных полей
    if not username:
        return False, "Ошибка: Имя пользователя обязательно"
    if not email:
        return False, "Ошибка: Email обязателен"
    if not password:
        return False, "Ошибка: Пароль обязателен"
        
    # Проверка длины имени пользователя
    if len(username) < 3:
        return False, "Ошибка: Имя пользователя должно содержать минимум 3 символа"
    if len(username) > 64:
        return False, "Ошибка: Имя пользователя не должно превышать 64 символа"
        
    # Проверка длины пароля
    if len(password) < 6:
        return False, "Ошибка: Пароль должен содержать минимум 6 символов"
        
    # Проверка валидности email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Ошибка: Некорректный формат email"
        
    # Проверка длины имени и фамилии (если они указаны)
    if first_name and len(first_name) > 64:
        return False, "Ошибка: Имя не должно превышать 64 символа"
    if last_name and len(last_name) > 64:
        return False, "Ошибка: Фамилия не должна превышать 64 символа"
    
    return True, None

def validate_login_data(username, password):
    """
    Валидация данных пользователя при входе.
    Возвращает кортеж (is_valid, error_message).
    """
    # Проверка обязательных полей
    if not username:
        return False, "Ошибка: Имя пользователя обязательно"
    if not password:
        return False, "Ошибка: Пароль обязателен"
    
    return True, None

def validate_post_data(content):
    """
    Валидация данных поста.
    Возвращает кортеж (is_valid, error_message).
    """
    if not content:
        return False, "Ошибка: Содержание поста не может быть пустым"
    if len(content) > 1000:
        return False, "Ошибка: Пост слишком длинный (максимум 1000 символов)"
    
    return True, None 
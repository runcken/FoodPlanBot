from datacenter.models import User


def add_new_user(message):
    chat_id = message.from_user.id
    if not User.objects.filter(chat_id=chat_id).exists():
        username = str(message.from_user.username)
        new_user = User(chat_id=chat_id, user_name=username)
        new_user.save()


def set_user_price(chat_id, price):
    """
    Устанавливает максимальную цену для пользователя
    """

    try:
        user = User.objects.get(chat_id=str(chat_id))
        user.price = price
        user.save()
        return True
    except User.DoesNotExist:
        return False


def get_user_budget(chat_id):
    user = User.objects.get(chat_id=chat_id)
    return user.price


def toggle_user_preference(chat_id, preference_type):
    """
    Функция для переключения ограничения пользователя
    Args:
        chat_id: ID чата пользователя (str)
        preference_type: тип ограничения ('gluten_free', 'vegan', 'eco')
    Returns:
        new_value: новое значение (True/False) и None если ошибка
    """
    # Находим пользователя по chat_id
    user = User.objects.get(chat_id=str(chat_id))

    # Меняем значение на противоположное
    current_value = getattr(user, preference_type)
    new_value = not current_value
    setattr(user, preference_type, new_value)

    # Сохраняем в базу данных
    user.save()
    return new_value


def get_user_filters_status(user):
    return {
        'gluten_free': user.gluten_free,
        'vegan': user.vegan,
        'eco': user.eco,
        'budget': user.price
    }
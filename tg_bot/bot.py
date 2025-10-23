from datacenter.models import Dish, User
import random

def toggle_user_preference(chat_id, preference_type):
    """
    Функция для переключения ограничения пользователя
    Args:
        chat_id: ID чата пользователя (str)
        preference_type: тип ограничения ('gluten_free', 'vegan', 'eco')
    Returns:
        new_value: новое значение (True/False) или None если ошибка
    """
    try:
        # Находим пользователя по chat_id
        user = User.objects.get(chat_id=str(chat_id))

        # Меняем значение на противоположное
        current_value = getattr(user, preference_type)
        new_value = not current_value
        setattr(user, preference_type, new_value)

        # Сохраняем в базу данных
        user.save()

        return new_value

def get_dish(chat_id):
    user = User.objects.get(chat_id=chat_id)
    filtered_dishes = Dish.objects.filter(
        gluten_free=user.gluten_free,
        vegan=user.vegan,
        eco=user.eco,
        price__lte=user.price,
    )
    return random.choice(filtered_dishes)


def run():
    print(Dish.objects.all())

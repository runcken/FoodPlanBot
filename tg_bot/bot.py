from datacenter.models import Dish, User
import random
import dotenv
import os
import telebot


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


def toggle_user_preference(chat_id, preference_type):
    """
    Функция для переключения ограничения пользователя
    Args:
        chat_id: ID чата пользователя (str)
        preference_type: тип ограничения ('gluten_free', 'vegan', 'eco')
    Returns:
        new_value: новое значение (True/False) или None если ошибка
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
    dotenv.load_dotenv()
    token = os.getenv("TG_BOT")

    bot = telebot.TeleBot(token)
    welcome_message = "🍽️ Добро пожаловать в FoodPlan!\nМы поможем вам выбрать, что приготовить сегодня — вкусно, просто и с пользой 💚\nНачнём с подбора блюда?"

    @bot.message_handler(commands=['start',])
    def send_welcome(message):
        chat_id = message.from_user.id
        add_new_user(message)
        bot.send_message(chat_id, welcome_message)

    error_message = "Извините, я вас не понял 😔 Пожалуйста, используйте кнопки меню или введите команду /menu."

    @bot.message_handler()
    def handle_text_message(message):
        if not message.text.startswith('/'):
            bot.send_message(message.chat.id, error_message)

    bot.infinity_polling()

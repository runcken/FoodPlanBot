import django
import os
import sys
import telebot

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FoodPlanDjango.settings')
django.setup()

from tg_bot.config import TOKEN
from tg_bot.handlers.message_handlers import setup_message_handlers
from tg_bot.handlers.callback_handlers import setup_callback_handlers


def run():
    bot = telebot.TeleBot(TOKEN)
    user_states = {}

    setup_message_handlers(bot, user_states)
    setup_callback_handlers(bot, user_states)

    print("Бот запущен...")
    bot.infinity_polling()


def main():
    run()


if __name__ == '__main__':
    run()
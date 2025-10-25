import os
import dotenv


dotenv.load_dotenv()

TOKEN = os.getenv("TG_BOT")
WELCOME_MESSAGE = "🍽 Добро пожаловать в FoodPlan!\nМы поможем вам выбрать, что приготовить сегодня — вкусно, просто и с пользой 💚\nНачнём с подбора блюда?"
ERROR_MESSAGE = "❌ Извините, я вас не понял 😔 Пожалуйста, используйте кнопки меню или введите команду /menu."
MAX_BUDGET = 2147483647

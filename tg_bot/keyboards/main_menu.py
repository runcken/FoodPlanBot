from telebot import types
from tg_bot.utils.formatters import format_budget_text


def get_start_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    menu_button = types.InlineKeyboardButton("Меню", callback_data="main_menu")
    keyboard.add(menu_button)
    return keyboard
    

def get_main_menu_keyboard(user):
    current_budget = user.price
    budget_text = format_budget_text(current_budget)
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    random_dish_button = types.InlineKeyboardButton("🎲 Случайное блюдо", callback_data="show_random_dish")
    budget_button = types.InlineKeyboardButton("💰 Установить бюджет", callback_data="set_budget")
    filters_button = types.InlineKeyboardButton("⚙️ Фильтры", callback_data="filters_menu")
    
    keyboard.add(random_dish_button)
    keyboard.add(budget_button)
    keyboard.add(filters_button)
    
    return keyboard, budget_text
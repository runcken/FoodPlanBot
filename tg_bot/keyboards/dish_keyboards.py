from telebot import types


def get_dish_keyboard(dish_id=None):
    """Создает клавиатуру для сообщения с блюдом"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    next_button = types.InlineKeyboardButton("🎲 Следующее блюдо", callback_data="next_dish")
    products_button = types.InlineKeyboardButton("🛒 Продукты", callback_data=f"products_{dish_id}")
    recipe_button = types.InlineKeyboardButton("📖 Рецепт", callback_data=f"recipe_{dish_id}")
    menu_button = types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
    
    keyboard.add(next_button)
    keyboard.add(products_button, recipe_button)
    keyboard.add(menu_button)
    
    return keyboard


def get_back_to_dish_keyboard(dish_id):
    """Создает клавиатуру для возврата к блюду"""
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("🔙 Назад к блюду", callback_data=f"back_to_dish_{dish_id}")
    keyboard.add(back_button)
    return keyboard


def get_budget_input_keyboard():
    """Создает клавиатуру меню бюджета"""
    keyboard = types.InlineKeyboardMarkup()
    cancel_button = types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_budget")
    keyboard.add(cancel_button)
    return keyboard
from telebot import types


def get_filters_menu_keyboard(user):
    """Создает клавиатуру меню фильтров"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    gluten_text = "✅ Без глютена" if user.gluten_free else "❌ Без глютена"
    vegan_text = "✅ Веганское" if user.vegan else "❌ Веганское"
    eco_text = "✅ ЭКО" if user.eco else "❌ ЭКО"
    
    gluten_button = types.InlineKeyboardButton(gluten_text, callback_data="toggle_gluten")
    vegan_button = types.InlineKeyboardButton(vegan_text, callback_data="toggle_vegan")
    eco_button = types.InlineKeyboardButton(eco_text, callback_data="toggle_eco")
    
    reset_button = types.InlineKeyboardButton("🔄 Сбросить все фильтры", callback_data="reset_filters")
    back_button = types.InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")
    
    keyboard.add(gluten_button, vegan_button, eco_button)
    keyboard.add(reset_button)
    keyboard.add(back_button)
    
    return keyboard
from datacenter.models import User
from tg_bot.utils import user_utils
from tg_bot.keyboards import main_menu


def handle_budget_input(bot, message, user_states):
    """Обрабатывает ввод бюджета пользователем"""
    chat_id = message.chat.id
    user_input = message.text.strip()
    
    # Сбрасываем состояние
    if chat_id in user_states:
        del user_states[chat_id]
    
    # Проверяем ввод
    try:
        # Убираем возможные нечисловые символы, кроме цифр
        budget = int(''.join(filter(str.isdigit, user_input)))
        
        if budget <= 0:
            bot.send_message(chat_id, "❌ Бюджет должен быть положительным числом.")
            return
        
        # Устанавливаем бюджет
        user_utils.set_user_price(chat_id, budget)
        
        # Показываем обновленное главное меню
        user = User.objects.get(chat_id=str(chat_id))
        keyboard, budget_text = main_menu.get_main_menu_keyboard(user)
        menu_text = f"🍽 *Главное меню*\n\n✅ Бюджет установлен: {budget}₽"
        bot.send_message(chat_id, menu_text, parse_mode='Markdown', reply_markup=keyboard)
        
    except ValueError:
        bot.send_message(chat_id, "❌ Пожалуйста, введите корректную сумму. Например: 500, 1000, 1500")
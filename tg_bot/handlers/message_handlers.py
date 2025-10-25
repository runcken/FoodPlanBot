from datacenter.models import User
from tg_bot.utils import user_utils
from tg_bot.keyboards import main_menu
from tg_bot.config import WELCOME_MESSAGE, ERROR_MESSAGE
from tg_bot.handlers.state_handlers import handle_budget_input


def setup_message_handlers(bot, user_states):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        chat_id = message.from_user.id
        user_utils.add_new_user(message)
        keyboard = main_menu.get_start_menu_keyboard()
        bot.send_message(chat_id, WELCOME_MESSAGE, reply_markup=keyboard)


    @bot.message_handler(commands=['menu'])
    def send_menu(message):
        chat_id = message.chat.id
        user = User.objects.get(chat_id=str(chat_id))
        keyboard, budget_text = main_menu.get_main_menu_keyboard(user)
        menu_text = f"🍽 *Главное меню*\n\n💰 Текущий бюджет: {budget_text}"
        bot.send_message(chat_id, menu_text, parse_mode='Markdown', reply_markup=keyboard)


    @bot.message_handler(commands=['set_budget'])
    def set_budget_command(message):
        chat_id = message.chat.id
        user_input = message.text.replace("/set_budget", "").strip()
        
        if not user_input:
            # Если бюджет не указан, переходим в режим ввода
            from tg_bot.handlers.callback_handlers import set_budget_handler
            callback = type('Callback', (), {
                'message': type('Message', (), {'chat': type('Chat', (), {'id': chat_id})})
            })()
            set_budget_handler(bot, callback, user_states)
            return
        
        try:
            budget = int(''.join(filter(str.isdigit, user_input)))
            if budget <= 0:
                bot.send_message(chat_id, "❌ Бюджет должен быть положительным числом.")
                return
            
            user_utils.set_user_price(chat_id, budget)
            user = User.objects.get(chat_id=str(chat_id))
            keyboard, budget_text = main_menu.get_main_menu_keyboard(user)
            menu_text = f"🍽 *Главное меню*\n\n✅ Бюджет установлен: {budget}₽"
            bot.send_message(chat_id, menu_text, parse_mode='Markdown', reply_markup=keyboard)
            
        except ValueError:
            bot.send_message(chat_id, "❌ Пожалуйста, введите корректную сумму. Например: /set_budget 500")


    @bot.message_handler(commands=['budget'])
    def check_budget(message):
        chat_id = message.chat.id
        budget = user_utils.get_user_budget(chat_id)
        const_part = "Чтобы изменить бюджет, введите /set_budget или нажмите кнопку '💰 Установить бюджет' в меню."
        if budget == 2147483647:
            bot.send_message(chat_id, f"✅ Ваш бюджет не ограничен. {const_part}", parse_mode='HTML')
            return
        bot.send_message(chat_id, f"💰 Ваш бюджет составляет {budget} рублей. {const_part}", parse_mode='HTML')


    @bot.message_handler(commands=['filters'])
    def show_filters_command(message):
        chat_id = message.chat.id
        user = User.objects.get(chat_id=str(chat_id))
        from tg_bot.utils.formatters import format_filters_status
        from tg_bot.keyboards.filters_keyboard import get_filters_menu_keyboard
        
        filters_status = format_filters_status(user)
        keyboard = get_filters_menu_keyboard(user)
        
        bot.send_message(
            chat_id,
            filters_status,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        

    @bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id] == "waiting_for_budget")
    def handle_budget_state_message(message):
        """Обрабатывает сообщения, когда пользователь в состоянии ожидания бюджета"""
        handle_budget_input(bot, message, user_states)

    @bot.message_handler()

    def handle_text_message(message):
        if not message.text.startswith('/'):
            # Проверяем, не находится ли пользователь в состоянии ожидания ввода бюджета
            if message.chat.id in user_states and user_states[message.chat.id] == "waiting_for_budget":
                handle_budget_state_message(message)
            else:
                keyboard = main_menu.get_start_menu_keyboard()
                bot.send_message(message.chat.id, ERROR_MESSAGE, reply_markup=keyboard)

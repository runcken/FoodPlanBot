import dotenv
import os
import random
import telebot
from telebot import types

from datacenter.models import Dish, User, DishProduct


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


def get_budget(message):
    chat_id = message.chat.id
    user = User.objects.get(chat_id=chat_id)
    return user.price


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
    
    filtered_dishes = Dish.objects.all()
    
    # Применяем фильтры только если они включены
    if user.gluten_free:
        filtered_dishes = filtered_dishes.filter(gluten_free=True)
    if user.vegan:
        filtered_dishes = filtered_dishes.filter(vegan=True)
    if user.eco:
        filtered_dishes = filtered_dishes.filter(eco=True)
    
    # Фильтр по бюджету
    filtered_dishes = filtered_dishes.filter(price__lte=user.price)
    
    if filtered_dishes.exists():
        return random.choice(filtered_dishes)
    else:
        raise Exception("No dishes found matching the criteria")


def format_dish_main(dish):
    """Форматирует основную информацию о блюде"""
    message = f"🍽 *{dish.title}*\n\n"
    
    if dish.description:
        message += f"📝 *Описание:* {dish.description}\n\n"
    
    message += "⚡ *Характеристики:*\n"
    message += f"   • Без глютена: {'✅' if dish.gluten_free else '❌'}\n"
    message += f"   • Веганское: {'✅' if dish.vegan else '❌'}\n"
    message += f"   • ЭКО: {'✅' if dish.eco else '❌'}\n\n"
    
    message += f"💰 *Цена:* {dish.price} руб."

    return message


def get_dish_products(dish):
    """Получает список продуктов для блюда"""
    dish_products = DishProduct.objects.filter(dish=dish)
    products_text = "🛒 *Продукты для этого блюда:*\n\n"
    
    for dp in dish_products:
        if dp.quantity > 0:
            products_text += f"• {dp.product.name} - {dp.quantity}г"
            if dp.note:
                products_text += f" ({dp.note})"
        if dp.quantity == 0:
            products_text += f"• {dp.product.name} - {dp.note}"
        products_text += "\n"
    
    return products_text


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


def get_main_menu_keyboard(chat_id):
    """Создает клавиатуру главного меню с информацией о текущем бюджете"""
    user = User.objects.get(chat_id=str(chat_id))
    
    # Получаем текущий бюджет пользователя
    current_budget = user.price
    budget_text = "не ограничен" if current_budget == 2147483647 else f"{current_budget}₽"
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Кнопка случайного блюда
    random_dish_button = types.InlineKeyboardButton("🎲 Случайное блюдо", callback_data="show_random_dish")
    
    # Кнопки меню
    budget_button = types.InlineKeyboardButton("💰 Установить бюджет", callback_data="set_budget")
    filters_button = types.InlineKeyboardButton("⚙️ Фильтры", callback_data="filters_menu")
    
    # Собираем клавиатуру
    keyboard.add(random_dish_button)
    keyboard.add(budget_button)
    keyboard.add(filters_button)
    
    return keyboard, budget_text


def get_filters_menu_keyboard(chat_id):
    """Создает клавиатуру меню фильтров"""
    user = User.objects.get(chat_id=str(chat_id))
    
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    # Кнопки фильтров с текущим состоянием
    gluten_text = "✅ Без глютена" if user.gluten_free else "❌ Без глютена"
    vegan_text = "✅ Веганское" if user.vegan else "❌ Веганское"
    eco_text = "✅ ЭКО" if user.eco else "❌ ЭКО"
    
    gluten_button = types.InlineKeyboardButton(gluten_text, callback_data="toggle_gluten")
    vegan_button = types.InlineKeyboardButton(vegan_text, callback_data="toggle_vegan")
    eco_button = types.InlineKeyboardButton(eco_text, callback_data="toggle_eco")
    
    # Кнопка сброса всех фильтров
    reset_button = types.InlineKeyboardButton("🔄 Сбросить все фильтры", callback_data="reset_filters")
    
    # Кнопка назад
    back_button = types.InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")
    
    keyboard.add(gluten_button, vegan_button, eco_button)
    keyboard.add(reset_button)
    keyboard.add(back_button)
    
    return keyboard


def format_filters_status(user):
    """Форматирует текущий статус фильтров"""
    status = "⚙️ *Текущие настройки фильтров:*\n\n"
    status += f"• Без глютена: {'✅ ВКЛ' if user.gluten_free else '❌ ВЫКЛ'}\n"
    status += f"• Веганское: {'✅ ВКЛ' if user.vegan else '❌ ВЫКЛ'}\n"
    status += f"• ЭКО: {'✅ ВКЛ' if user.eco else '❌ ВЫКЛ'}\n\n"
    status += "Нажмите на фильтр, чтобы переключить его состояние."
    
    return status


# Словарь для хранения состояний пользователей (ожидают ввода бюджета)
user_states = {}


def run():
    dotenv.load_dotenv()
    token = os.getenv("TG_BOT")

    bot = telebot.TeleBot(token)
    welcome_message = "🍽 Добро пожаловать в FoodPlan!\nМы поможем вам выбрать, что приготовить сегодня — вкусно, просто и с пользой 💚\nНачнём с подбора блюда?"

    start_menu_keyboard = types.InlineKeyboardMarkup()
    menu_button = types.InlineKeyboardButton("Меню", callback_data="main_menu")
    start_menu_keyboard.add(menu_button)

    @bot.callback_query_handler(func=lambda call: call.data == "show_random_dish")
    def show_random_dish_handler(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        try:
            dish = get_dish(chat_id)
            dish_message = format_dish_main(dish)
            keyboard = get_dish_keyboard(dish.id)
            
            # Если есть изображение, отправляем его с подписью
            if dish.image:
                try:
                    bot.send_photo(
                        chat_id, 
                        dish.image, 
                        caption=dish_message, 
                        parse_mode='Markdown',
                        reply_markup=keyboard
                    )
                except Exception as photo_error:
                    print(f"Photo send error: {photo_error}")
                    # Если не удалось отправить фото, отправляем текстовое сообщение
                    bot.send_message(
                        chat_id, 
                        dish_message, 
                        parse_mode='Markdown',
                        reply_markup=keyboard
                    )
            else:
                bot.send_message(
                    chat_id, 
                    dish_message, 
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
        except Exception as e:
            print(f"Error: {e}")
            # Получаем текущий бюджет для информативного сообщения
            user = User.objects.get(chat_id=str(chat_id))
            budget_text = "не ограничен" if user.price == 2147483647 else f"{user.price}₽"
            
            error_message = f"😔 К сожалению, не удалось найти подходящее блюдо.\n\n"
            error_message += f"*Текущие настройки:*\n"
            error_message += f"• Бюджет: {budget_text}\n"
            error_message += f"• Без глютена: {'✅' if user.gluten_free else '❌'}\n"
            error_message += f"• Веганское: {'✅' if user.vegan else '❌'}\n"
            error_message += f"• ЭКО: {'✅' if user.eco else '❌'}\n\n"
            error_message += "Попробуйте изменить фильтры или бюджет."
            
            keyboard, _ = get_main_menu_keyboard(chat_id)
            bot.send_message(
                chat_id, 
                error_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )

    @bot.callback_query_handler(func=lambda call: call.data == "next_dish")
    def next_dish_handler(call: types.CallbackQuery):
        # Вызываем тот же обработчик, что и для показа случайного блюда
        show_random_dish_handler(call)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("products_"))
    def show_products_handler(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        dish_id = call.data.split("_")[1]
        
        try:
            dish = Dish.objects.get(id=dish_id)
            products_message = get_dish_products(dish)
            keyboard = get_back_to_dish_keyboard(dish.id)
            
            bot.send_message(
                chat_id,
                products_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
        except Dish.DoesNotExist:
            bot.send_message(chat_id, "❌ Блюдо не найдено.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("recipe_"))
    def show_recipe_handler(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        dish_id = call.data.split("_")[1]
        
        try:
            dish = Dish.objects.get(id=dish_id)
            recipe_message = f"📖 *Рецепт {dish.title}:*\n\n{dish.recipe}"
            keyboard = get_back_to_dish_keyboard(dish.id)
            
            bot.send_message(
                chat_id,
                recipe_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
        except Dish.DoesNotExist:
            bot.send_message(chat_id, "❌ Блюдо не найдено.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_dish_"))
    def back_to_dish_handler(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        dish_id = call.data.split("_")[3]  # back_to_dish_{id}
        
        try:
            dish = Dish.objects.get(id=dish_id)
            dish_message = format_dish_main(dish)
            keyboard = get_dish_keyboard(dish.id)
            
            # Редактируем текущее сообщение
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=dish_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
        except Dish.DoesNotExist:
            bot.send_message(chat_id, "❌ Блюдо не найдено.")
        except Exception as e:
            print(f"Error editing message: {e}")
            # Если не удалось отредактировать, отправляем новое
            bot.send_message(
                chat_id,
                dish_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )

    @bot.callback_query_handler(func=lambda call: call.data == "set_budget")
    def set_budget_handler(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        
        # Устанавливаем состояние ожидания ввода бюджета
        user_states[chat_id] = "waiting_for_budget"
        
        # Отправляем сообщение с инструкцией
        keyboard = types.InlineKeyboardMarkup()
        cancel_button = types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_budget")
        keyboard.add(cancel_button)
        
        bot.send_message(
            chat_id,
            "💰 *Установите бюджет*\n\nВведите сумму в рублях, которую вы готовы потратить на блюдо.\n\nНапример: 500, 1000, 1500",
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data == "cancel_budget")
    def cancel_budget_handler(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        
        # Сбрасываем состояние
        if chat_id in user_states:
            del user_states[chat_id]
        
        # Возвращаем в главное меню
        keyboard, budget_text = get_main_menu_keyboard(chat_id)
        menu_text = f"🍽 *Главное меню*\n\n💰 Текущий бюджет: {budget_text}"
        
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=menu_text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Error editing message: {e}")
            bot.send_message(
                chat_id,
                menu_text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )

    @bot.callback_query_handler(func=lambda call: call.data == "filters_menu")
    def filters_menu_handler(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        user = User.objects.get(chat_id=str(chat_id))
        
        filters_status = format_filters_status(user)
        keyboard = get_filters_menu_keyboard(chat_id)
        
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=filters_status,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Error editing message: {e}")
            bot.send_message(
                chat_id,
                filters_status,
                parse_mode='Markdown',
                reply_markup=keyboard
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_"))
    def toggle_filter_handler(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        filter_type = call.data.split("_")[1]  # toggle_{filter_type}
        
        # Определяем поле в модели User по типу фильтра
        field_map = {
            "gluten": "gluten_free",
            "vegan": "vegan",
            "eco": "eco"
        }
        
        if filter_type in field_map:
            field_name = field_map[filter_type]
            new_value = toggle_user_preference(chat_id, field_name)
            
            # Обновляем сообщение с фильтрами
            user = User.objects.get(chat_id=str(chat_id))
            filters_status = format_filters_status(user)
            keyboard = get_filters_menu_keyboard(chat_id)
            
            # Добавляем сообщение об изменении
            filter_names = {
                "gluten": "Без глютена",
                "vegan": "Веганское", 
                "eco": "ЭКО"
            }
            
            status_text = "✅ ВКЛ" if new_value else "❌ ВЫКЛ"
            action_message = f"Фильтр '{filter_names[filter_type]}' теперь {status_text}"
            
            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text=f"{filters_status}\n\n{action_message}",
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Error editing message: {e}")
                bot.send_message(
                    chat_id,
                    f"{filters_status}\n\n{action_message}",
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )

    @bot.callback_query_handler(func=lambda call: call.data == "reset_filters")
    def reset_filters_handler(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        
        # Сбрасываем все фильтры
        user = User.objects.get(chat_id=str(chat_id))
        user.gluten_free = False
        user.vegan = False
        user.eco = False
        user.save()
        
        # Обновляем сообщение с фильтрами
        filters_status = format_filters_status(user)
        keyboard = get_filters_menu_keyboard(chat_id)
        
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"{filters_status}\n\n✅ Все фильтры сброшены!",
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Error editing message: {e}")
            bot.send_message(
                chat_id,
                f"{filters_status}\n\n✅ Все фильтры сброшены!",
                parse_mode='Markdown',
                reply_markup=keyboard
            )

    @bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id] == "waiting_for_budget")
    def handle_budget_input(message):
        chat_id = message.chat.id
        user_input = message.text.strip()
        
        # Сбрасываем состояние
        del user_states[chat_id]
        
        # Проверяем ввод
        try:
            # Убираем возможные нечисловые символы, кроме цифр
            budget = int(''.join(filter(str.isdigit, user_input)))
            
            if budget <= 0:
                bot.send_message(chat_id, "❌ Бюджет должен быть положительным числом.")
                return
            
            # Устанавливаем бюджет
            set_user_price(chat_id, budget)
            
            # Показываем обновленное главное меню
            keyboard, budget_text = get_main_menu_keyboard(chat_id)
            menu_text = f"🍽 *Главное меню*\n\n✅ Бюджет установлен: {budget}₽"
            bot.send_message(chat_id, menu_text, parse_mode='Markdown', reply_markup=keyboard)
            
        except ValueError:
            bot.send_message(chat_id, "❌ Пожалуйста, введите корректную сумму. Например: 500, 1000, 1500")

    @bot.message_handler(commands=['start'])
    def send_welcome(message: types.Message):
        chat_id = message.from_user.id
        add_new_user(message)
        bot.send_message(chat_id, welcome_message, reply_markup=start_menu_keyboard)

    @bot.callback_query_handler(func=lambda call: call.data == "main_menu")
    def main_menu_handler(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        keyboard, budget_text = get_main_menu_keyboard(chat_id)
        menu_text = f"🍽 *Главное меню*\n\n💰 Текущий бюджет: {budget_text}"
        
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=menu_text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        except:
            bot.send_message(
                chat_id,
                menu_text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )

    @bot.message_handler(commands=['menu'])
    def send_menu(message: types.Message):
        chat_id = message.chat.id
        keyboard, budget_text = get_main_menu_keyboard(chat_id)
        menu_text = f"🍽 *Главное меню*\n\n💰 Текущий бюджет: {budget_text}"
        bot.send_message(chat_id, menu_text, parse_mode='Markdown', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call: types.CallbackQuery):
        # Этот обработчик теперь обрабатывает только оставшиеся callback_data
        chat_id = call.message.chat.id
        if call.data == "budget":
            check_budget(call.message)

    @bot.message_handler(commands=['set_budget'])
    def set_budget_command(message: types.Message):
        chat_id = message.chat.id
        user_input = message.text.replace("/set_budget", "").strip()
        
        if not user_input:
            # Если бюджет не указан, переходим в режим ввода
            set_budget_handler(type('Callback', (), {'message': type('Message', (), {'chat': type('Chat', (), {'id': chat_id})})})())
            return
        
        # Проверяем ввод
        try:
            # Убираем возможные нечисловые символы, кроме цифр
            budget = int(''.join(filter(str.isdigit, user_input)))
            
            if budget <= 0:
                bot.send_message(chat_id, "❌ Бюджет должен быть положительным числом.")
                return
            
            # Устанавливаем бюджет
            set_user_price(chat_id, budget)
            
            # Показываем обновленное главное меню
            keyboard, budget_text = get_main_menu_keyboard(chat_id)
            menu_text = f"🍽 *Главное меню*\n\n✅ Бюджет установлен: {budget}₽"
            bot.send_message(chat_id, menu_text, parse_mode='Markdown', reply_markup=keyboard)
            
        except ValueError:
            bot.send_message(chat_id, "❌ Пожалуйста, введите корректную сумму. Например: /set_budget 500")

    @bot.message_handler(commands=['budget'])
    def check_budget(message: types.Message):
        chat_id = message.chat.id
        budget = get_budget(message)
        const_part = "Чтобы изменить бюджет, введите /set_budget или нажмите кнопку '💰 Установить бюджет' в меню."
        if budget == 2147483647:
            bot.send_message(chat_id, f"✅ Ваш бюджет не ограничен. {const_part}", parse_mode='HTML')
            return
        bot.send_message(chat_id, f"💰 Ваш бюджет составляет {budget} рублей. {const_part}", parse_mode='HTML')

    @bot.message_handler(commands=['filters'])
    def show_filters_command(message: types.Message):
        chat_id = message.chat.id
        user = User.objects.get(chat_id=str(chat_id))
        
        filters_status = format_filters_status(user)
        keyboard = get_filters_menu_keyboard(chat_id)
        
        bot.send_message(
            chat_id,
            filters_status,
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    error_message = "❌ Извините, я вас не понял 😔 Пожалуйста, используйте кнопки меню или введите команду /menu."

    @bot.message_handler()
    def handle_text_message(message: types.Message):
        if not message.text.startswith('/'):
            # Проверяем, не находится ли пользователь в состоянии ожидания ввода бюджета
            if message.chat.id in user_states and user_states[message.chat.id] == "waiting_for_budget":
                handle_budget_input(message)
            else:
                bot.send_message(message.chat.id, error_message, reply_markup=start_menu_keyboard)

    print('Бот запущен...')
    bot.infinity_polling()
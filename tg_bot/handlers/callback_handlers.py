from datacenter.models import Dish, User
from tg_bot.utils import user_utils, dish_utils, formatters
from tg_bot.keyboards import main_menu, dish_keyboards, filters_keyboard


def setup_callback_handlers(bot, user_states):
    @bot.callback_query_handler(func=lambda call: call.data == "show_random_dish")
    def show_random_dish_handler(call):
        chat_id = call.message.chat.id
        try:
            dish = dish_utils.get_dish(chat_id)
            dish_message = formatters.format_dish_main(dish)
            keyboard = dish_keyboards.get_dish_keyboard(dish.id)
            
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
            budget_text = formatters.format_budget_text(user.price)
            
            error_message = f"😔 К сожалению, не удалось найти подходящее блюдо.\n\n"
            error_message += f"*Текущие настройки:*\n"
            error_message += f"• Бюджет: {budget_text}\n"
            error_message += f"• Без глютена: {'✅' if user.gluten_free else '❌'}\n"
            error_message += f"• Веганское: {'✅' if user.vegan else '❌'}\n"
            error_message += f"• ЭКО: {'✅' if user.eco else '❌'}\n\n"
            error_message += "Попробуйте изменить фильтры или бюджет."
            
            keyboard, _ = main_menu.get_main_menu_keyboard(user)
            bot.send_message(
                chat_id, 
                error_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )


    @bot.callback_query_handler(func=lambda call: call.data == "next_dish")
    def next_dish_handler(call):
        # Вызываем обработчик для показа случайного блюда
        show_random_dish_handler(call)


    @bot.callback_query_handler(func=lambda call: call.data.startswith("products_"))
    def show_products_handler(call):
        chat_id = call.message.chat.id
        dish_id = call.data.split("_")[1]
        
        try:
            dish = Dish.objects.get(id=dish_id)
            products_message = dish_utils.get_dish_products(dish)
            keyboard = dish_keyboards.get_back_to_dish_keyboard(dish.id)
            
            bot.send_message(
                chat_id,
                products_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
        except Dish.DoesNotExist:
            bot.send_message(chat_id, "❌ Блюдо не найдено.")


    @bot.callback_query_handler(func=lambda call: call.data.startswith("recipe_"))
    def show_recipe_handler(call):
        chat_id = call.message.chat.id
        dish_id = call.data.split("_")[1]
        
        try:
            dish = Dish.objects.get(id=dish_id)
            recipe_message = f"📖 *Рецепт {dish.title}:*\n\n{dish.recipe}"
            keyboard = dish_keyboards.get_back_to_dish_keyboard(dish.id)
            
            bot.send_message(
                chat_id,
                recipe_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
        except Dish.DoesNotExist:
            bot.send_message(chat_id, "❌ Блюдо не найдено.")


    @bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_dish_"))
    def back_to_dish_handler(call):
        chat_id = call.message.chat.id
        dish_id = call.data.split("_")[3]
        
        try:
            dish = Dish.objects.get(id=dish_id)
            dish_message = formatters.format_dish_main(dish)
            keyboard = dish_keyboards.get_dish_keyboard(dish.id)
            
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
            bot.send_message(
                chat_id,
                dish_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )


    @bot.callback_query_handler(func=lambda call: call.data == "set_budget")
    def set_budget_handler(call, user_states=user_states):
        chat_id = call.message.chat.id
        user_states[chat_id] = "waiting_for_budget"
        
        keyboard = dish_keyboards.get_budget_input_keyboard()
        
        bot.send_message(
            chat_id,
            "💰 *Установите бюджет*\n\nВведите сумму в рублях, которую вы готовы потратить на блюдо.\n\nНапример: 500, 1000, 1500",
            parse_mode='Markdown',
            reply_markup=keyboard
        )


    @bot.callback_query_handler(func=lambda call: call.data == "cancel_budget")
    def cancel_budget_handler(call):
        chat_id = call.message.chat.id
        
        if chat_id in user_states:
            del user_states[chat_id]
        
        user = User.objects.get(chat_id=str(chat_id))
        keyboard, budget_text = main_menu.get_main_menu_keyboard(user)
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
    def filters_menu_handler(call):
        chat_id = call.message.chat.id
        user = User.objects.get(chat_id=str(chat_id))
        
        filters_status = formatters.format_filters_status(user)
        keyboard = filters_keyboard.get_filters_menu_keyboard(user)
        
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
    def toggle_filter_handler(call):
        chat_id = call.message.chat.id
        filter_type = call.data.split("_")[1]
        
        field_map = {
            "gluten": "gluten_free",
            "vegan": "vegan",
            "eco": "eco"
        }
        
        if filter_type in field_map:
            field_name = field_map[filter_type]
            new_value = user_utils.toggle_user_preference(chat_id, field_name)
            
            user = User.objects.get(chat_id=str(chat_id))
            filters_status = formatters.format_filters_status(user)
            keyboard = filters_keyboard.get_filters_menu_keyboard(user)
            
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
    def reset_filters_handler(call):
        chat_id = call.message.chat.id
        
        user = User.objects.get(chat_id=str(chat_id))
        user.gluten_free = False
        user.vegan = False
        user.eco = False
        user.save()
        
        filters_status = formatters.format_filters_status(user)
        keyboard = filters_keyboard.get_filters_menu_keyboard(user)
        
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


    @bot.callback_query_handler(func=lambda call: call.data == "main_menu")
    def main_menu_handler(call):
        chat_id = call.message.chat.id
        user = User.objects.get(chat_id=str(chat_id))
        keyboard, budget_text = main_menu.get_main_menu_keyboard(user)
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

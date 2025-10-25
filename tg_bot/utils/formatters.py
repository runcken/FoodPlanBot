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


def format_filters_status(user):
    """Форматирует текущий статус фильтров"""
    status = "⚙️ *Текущие настройки фильтров:*\n\n"
    status += f"• Без глютена: {'✅ ВКЛ' if user.gluten_free else '❌ ВЫКЛ'}\n"
    status += f"• Веганское: {'✅ ВКЛ' if user.vegan else '❌ ВЫКЛ'}\n"
    status += f"• ЭКО: {'✅ ВКЛ' if user.eco else '❌ ВЫКЛ'}\n\n"
    status += "Нажмите на фильтр, чтобы переключить его состояние."
    return status


def format_budget_text(budget):
    return "не ограничен" if budget == 2147483647 else f"{budget}₽"
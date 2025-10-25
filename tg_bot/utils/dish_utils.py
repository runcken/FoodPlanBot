import random

from datacenter.models import Dish, User, DishProduct


def get_dish(chat_id):
    user = User.objects.get(chat_id=chat_id)

    # Применяем фильтры только если они включены
    filtered_dishes = Dish.objects.all()
    
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
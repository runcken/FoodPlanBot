from datacenter.models import Dish, User
import random


def get_dish(chat_id):
    user = User.objects.get(chat_id=chat_id)
    filtered_dishes = Dish.objects.filter(
        gluten_free=user.gluten_free,
        vegan=user.vegan,
        eco=user.eco,
        price__lte=user.price,
    )
    return random.choice(filtered_dishes)


def run():
    print(Dish.objects.all())

from datacenter.models import Dish


def run():
    print(Dish.objects.all())

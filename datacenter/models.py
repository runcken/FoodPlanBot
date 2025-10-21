from django.db import models

# Create your models here.


class Dish(models.Model):
    title = models.CharField(("Название блюда"), max_length=50)
    description = models.TextField("Описание", blank=True, default="")
    image = models.ImageField(("Изображение"), blank=True, null=True)
    gluten_free = models.BooleanField(("Без глютена"), default=False)
    vegan = models.BooleanField(("Веганское"), default=False)
    eco = models.BooleanField(("ЭКО"), default=False)
    price = models.IntegerField(("Цена"))

    def __str__(self):
        return self.title


class User(models.Model):
    user_name = models.CharField(("Имя пользователя"), max_length=50)
    chat_id = models.CharField(max_length=50)

    def __str__(self):
        return self.user_name

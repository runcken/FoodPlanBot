from django.db import models


class Dish(models.Model):
    title = models.CharField("Название блюда", max_length=100)
    description = models.TextField("Описание", blank=True, default="")
    image = models.ImageField("Изображение", blank=True, null=True)
    ingredients = models.TextField("Продукты", blank=True, null=True)
    gluten_free = models.BooleanField("Без глютена", default=False)
    vegan = models.BooleanField("Веганское", default=False)
    eco = models.BooleanField("ЭКО", default=False)
    recipe = models.TextField("Рецепт")
    price = models.PositiveIntegerField("Цена", default=0)  # Цена блюда

    class Meta:
        ordering = ('title',)
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'

    def __str__(self):
        return self.title


class User(models.Model):
    user_name = models.CharField("Имя пользователя", max_length=50)
    chat_id = models.CharField(max_length=50)
    gluten_free = models.BooleanField("Без глютена", default=False)
    vegan = models.BooleanField("Веганское", default=False)
    eco = models.BooleanField("ЭКО", default=False)
    price = models.PositiveIntegerField("Цена", blank=True, null=True)

    class Meta:
        ordering = ('user_name',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.user_name


class Product(models.Model):
    name = models.CharField("Название продукта", max_length=100)
    price = models.PositiveIntegerField("Цена за 100 грамм", default=0)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name


class DishProduct(models.Model):
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='product_dish',
        verbose_name='Блюдо',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name='Масса в граммах')

    class Meta:
        ordering = ('dish',)
        verbose_name = 'Продукт и цена'
        verbose_name_plural = 'Продукты и цена'

    def __str__(self):
        return f'{self.dish.title} - {self.product.name}'

    @property
    def price(self):
        """Цена ингредиента по массе"""
        return self.product.price * self.quantity // 100

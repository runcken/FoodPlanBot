from django.contrib import admin
from .models import Dish, User, DishProduct,Product

class DishProductInline(admin.TabularInline):
    model = DishProduct
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'gluten_free', 'vegan', 'eco']
    list_filter = ['gluten_free', 'vegan', 'eco',]
    search_fields = ['title', 'description',]
    inlines = (DishProductInline,)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        dish = form.instance
        total = sum(dp.price for dp in dish.product_dish.all())
        dish.price = total
        dish.save(update_fields=['price'])

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'chat_id', 'gluten_free', 'vegan', 'eco', 'price' ]
    list_filter = ['gluten_free', 'vegan', 'eco']
    search_fields = ['user_name', 'gluten_free', 'vegan', 'eco', 'chat_id']

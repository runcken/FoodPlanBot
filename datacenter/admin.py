from django.contrib import admin
from django.utils.html import format_html
from .models import Dish, User, DishProduct, Product


class DishProductInline(admin.TabularInline):
    model = DishProduct
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'price', 'gluten_free', 'vegan', 'eco']
    list_display_links = ('image_preview', 'title')
    list_filter = ['gluten_free', 'vegan', 'eco',]
    search_fields = ['title', 'description',]
    inlines = (DishProductInline,)
    readonly_fields = ['price', 'image_preview']
    fields = ('title', 'description', "recipe", 'image', 'image_preview', 'vegan', 'eco', 'gluten_free', 'price')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Фото"

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        dish = form.instance
        total = sum(dp.price for dp in dish.product_dish.all())
        dish.price = total
        dish.save(update_fields=['price'])


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'chat_id', 'gluten_free', 'vegan', 'eco', 'price']
    list_filter = ['gluten_free', 'vegan', 'eco']
    search_fields = ['user_name', 'gluten_free', 'vegan', 'eco', 'chat_id']

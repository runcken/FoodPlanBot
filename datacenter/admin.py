from django.contrib import admin
from .models import Dish, User

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['title', 'gluten_free', 'vegan', 'eco' , 'price']
    list_filter = ['gluten_free', 'vegan', 'eco']
    search_fields = ['title', 'gluten_free', 'vegan', 'eco', 'description']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'chat_id', 'gluten_free', 'vegan', 'eco', 'price' ]
    list_filter = ['gluten_free', 'vegan', 'eco']
    search_fields = ['user_name', 'gluten_free', 'vegan', 'eco', 'chat_id']

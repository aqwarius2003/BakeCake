from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Cake, Order, Client


# Расширяем стандартную админку User
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    # Добавляем связанные заказы в детальном просмотре пользователя
    fieldsets = UserAdmin.fieldsets + (
        ('Заказы', {'fields': ()}),
    )

    def view_orders(self, obj):
        return f"{obj.order_set.count()} заказов"

    view_orders.short_description = "Количество заказов"


# Перерегистрируем модель User с нашей кастомной админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_info', 'cake_info', 'delivery_date', 'status', 'total_price')
    list_filter = ('status', 'delivery_date', 'created_at')
    search_fields = ('client__name', 'client__phone', 'address')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Клиент и заказ', {
            'fields': ('client', 'cake', 'status', 'total_price')
        }),
        ('Информация о доставке', {
            'fields': ('delivery_date', 'delivery_time', 'address', 'comment')
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def client_info(self, obj):
        from django.utils.html import format_html
        return format_html(
            '<div><strong>{}</strong><br>{}</div>',
            obj.client.name,
            obj.client.phone
        )

    client_info.short_description = 'Клиент'

    def cake_info(self, obj):
        return f"{obj.cake.levels} уровня, {obj.cake.get_shape_display()}"

    cake_info.short_description = 'Торт'


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('id', 'levels', 'shape', 'topping', 'berries', 'decor', 'inscription')
    list_filter = ('levels', 'shape', 'topping', 'berries', 'decor')
    search_fields = ('inscription',)

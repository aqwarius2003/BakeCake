from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Cake, Order, Client, SettingsManager, ShortLink


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


@admin.register(SettingsManager)
class SettingsManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_token_masked', 'telegram_chat_id', 'vk_token_masked')
    
    def has_add_permission(self, request):
        # Запрещаем создание новых настроек, если они уже существуют
        return not SettingsManager.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление настроек
        return False
    
    def telegram_token_masked(self, obj):
        if not obj.telegram_token:
            return "Не установлен"
        # Показываем только первые и последние 4 символа токена
        masked = f"{obj.telegram_token[:4]}...{obj.telegram_token[-4:]}" if len(obj.telegram_token) > 8 else "****"
        return masked
    
    def vk_token_masked(self, obj):
        if not obj.vk_token:
            return "Не установлен"
        # Показываем только первые и последние 4 символа токена
        masked = f"{obj.vk_token[:4]}...{obj.vk_token[-4:]}" if len(obj.vk_token) > 8 else "****"
        return masked
    
    telegram_token_masked.short_description = "Токен Telegram"
    vk_token_masked.short_description = "Токен ВКонтакте"


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('truncated_original_url', 'display_short_link', 'get_clicks_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('short_code', 'original_url')
    readonly_fields = ('short_code', 'created_at', 'get_clicks_count')
    fields = ('original_url', 'short_code', 'get_clicks_count', 'created_at')
    
    def truncated_original_url(self, obj):
        """Возвращает укороченную версию оригинального URL для отображения в админке"""
        max_length = 50
        return (obj.original_url[:max_length] + '...') if len(obj.original_url) > max_length else obj.original_url
    
    def display_short_link(self, obj):
        """Формирует и отображает короткую ссылку VK"""
        from django.utils.html import format_html
        
        # Короткая ссылка VK
        if not obj.short_code.startswith('vk'):
            return "Не удалось создать"
            
        short_url = f"https://vk.cc/{obj.short_code.replace('vk', '')}"
        
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            short_url,
            short_url
        )
    
    def get_clicks_count(self, obj):
        """Получает количество переходов по короткой ссылке VK"""
        from .api_services import count_vk_clicks
        
        if not obj.short_code.startswith('vk'):
            return 0
            
        vk_url = f"https://vk.cc/{obj.short_code.replace('vk', '')}"
        return count_vk_clicks(vk_url)
    
    def save_model(self, request, obj, form, change):
        """
        При сохранении модели генерирует короткую ссылку через VK API
        """
        if not change:  # Только для новых объектов
            from .api_services import get_vk_short_link
            from urllib.parse import urlsplit
            
            # Создаем короткую ссылку через VK API
            vk_url = get_vk_short_link(obj.original_url)
            
            # Если вернулся оригинальный URL, значит ошибка или не настроен токен
            if vk_url == obj.original_url:
                obj.short_code = "не_создано"
            else:
                # Извлекаем код из URL VK
                url_parts = urlsplit(vk_url)
                obj.short_code = f"vk{url_parts.path.strip('/')}"
        
        super().save_model(request, obj, form, change)
    
    truncated_original_url.short_description = "Оригинальный URL"
    display_short_link.short_description = "Короткая ссылка VK"
    get_clicks_count.short_description = "Переходы"


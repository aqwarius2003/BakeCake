from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils import timezone


class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя клиента",
                            default="Не указано")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата регистрации")

    def __str__(self):
        return f"{self.name} ({self.phone})"

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-created_at']


class Cake(models.Model):
    LEVEL_CHOICES = [
        (1, "1 уровень (+400р)"),
        (2, "2 уровня (+750р)"),
        (3, "3 уровня (+1100р)")
    ]

    SHAPE_CHOICES = [
        ('circle', 'Круг'),
        ('square', 'Квадрат'),
        ('rectangle', 'Прямоугольник'),
    ]

    TOPPING_CHOICES = [
        ('none', 'Без'),
        ('white_sauce', 'Белый соус'),
        ('caramel_syrup', 'Карамельный'),
        ('maple_syrup', 'Кленовый'),
        ('blueberry_syrup', 'Черничный'),
        ('milk_chocolate', 'Молочный шоколад'),
        ('strawberry_syrup', 'Клубничный'),
    ]

    BERRY_CHOICES = [
        (1, 'Ежевика'),
        (2, 'Малина'),
        (3, 'Голубика'),
        (4, 'Клубника'),
    ]

    DECOR_CHOICES = [
        (1, 'Фисташки'),
        (2, 'Безе'),
        (3, 'Фундук'),
        (4, 'Пекан'),
        (5, 'Маршмеллоу'),
        (6, 'Марципан'),
    ]

    levels = models.IntegerField(choices=LEVEL_CHOICES,
                                 verbose_name="Количество уровней")
    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES, verbose_name="Форма")
    topping = models.CharField(max_length=20, choices=TOPPING_CHOICES,
                               verbose_name="Топпинг")
    berries = models.IntegerField(choices=BERRY_CHOICES, null=True, blank=True,
                                  verbose_name="Ягоды")
    decor = models.IntegerField(choices=DECOR_CHOICES, null=True, blank=True,
                                verbose_name="Декор")
    inscription = models.CharField(max_length=200, null=True, blank=True,
                                   verbose_name="Надпись")

    def __str__(self):
        return f"Торт {self.levels} уровня, {self.shape} форма"

    def get_price(self, is_urgent=False):
        base_price = 0
        # Цены соответствуют значениям из CHOICES
        level_prices = {1: 400, 2: 750, 3: 1100}
        shape_prices = {
            'circle': 600,
            'square': 400,
            'rectangle': 1000
        }
        topping_prices = {
            'none': 0,
            'white_sauce': 200,
            'caramel_syrup': 180,
            'maple_syrup': 200,
            'blueberry_syrup': 300,
            'milk_chocolate': 350,
            'strawberry_syrup': 200
        }
        berry_prices = {1: 400, 2: 300, 3: 450, 4: 500}
        decor_prices = {1: 300, 2: 400, 3: 350, 4: 300, 5: 200, 6: 280}

        base_price += level_prices.get(self.levels, 0)
        base_price += shape_prices.get(self.shape, 0)
        base_price += topping_prices.get(self.topping, 0)

        if self.berries:
            base_price += berry_prices.get(self.berries, 0)
        if self.decor:
            base_price += decor_prices.get(self.decor, 0)
        if self.inscription:
            base_price += 500

        if is_urgent:
            base_price *= 1.2  # Наценка 20% для срочных заказов

        return base_price

    class Meta:
        verbose_name = 'Торт'
        verbose_name_plural = 'Торты'
        ordering = ['-id']


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Новый"),
        ("confirmed", "Подтвержден"),
        ("preparing", "Готовится"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен")
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE, verbose_name="Торт")
    address = models.CharField(max_length=200, verbose_name="Адрес доставки")
    comment = models.TextField(null=True, blank=True,
                               verbose_name="Комментарий к заказу")
    delivery_date = models.DateField(verbose_name="Дата доставки")
    delivery_time = models.TimeField(verbose_name="Время доставки")
    total_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      verbose_name="Итоговая цена")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new",
                              verbose_name="Статус заказа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")

    def __str__(self):
        return f"Заказ {self.id} от {self.client.name}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.cake.get_price()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']


class SettingsManager(models.Model):
    """
    Класс-менеджер для хранения настроек телеграм-бота, ВКонтакте и управления сокращенными ссылками.
    """
    # Настройки Telegram
    telegram_token = models.CharField(max_length=255, verbose_name="Токен Telegram бота")
    telegram_chat_id = models.CharField(max_length=100, verbose_name="ID чата Telegram")
    
    # Настройки ВКонтакте
    vk_token = models.CharField(max_length=255, verbose_name="Токен ВКонтакте")
    
    class Meta:
        verbose_name = 'Настройки'
        verbose_name_plural = 'Настройки'
    
    def save(self, *args, **kwargs):
        # Гарантируем, что в таблице будет только одна запись
        if not self.pk and SettingsManager.objects.exists():
            # Если запись уже существует, просто обновляем её
            self.pk = SettingsManager.objects.first().pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Получить настройки или создать их с пустыми значениями"""
        settings_obj, created = cls.objects.get_or_create(
            defaults={
                'telegram_token': '',
                'telegram_chat_id': '',
                'vk_token': ''
            }
        )
        return settings_obj
    
    @classmethod
    def get_telegram_settings(cls):
        """Получить настройки телеграма"""
        settings = cls.get_settings()
        return settings.telegram_token, settings.telegram_chat_id
    
    @classmethod
    def get_vk_token(cls):
        """Получить токен ВКонтакте"""
        settings = cls.get_settings()
        return settings.vk_token


class ShortLink(models.Model):
    """
    Модель для хранения коротких ссылок и отслеживания переходов по ним.
    """
    original_url = models.URLField(max_length=2000, verbose_name="Оригинальная ссылка")
    short_code = models.CharField(max_length=10, unique=True, verbose_name="Короткий код")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.short_code} -> {self.original_url[:50]}..."
    
    @classmethod
    def create_short_link(cls, original_url):
        """Создать короткую ссылку для оригинального URL"""
        # Генерируем уникальный короткий код
        while True:
            # Создаем случайный код из букв и цифр
            short_code = ''.join(random.choice(string.ascii_letters + string.digits) 
                              for _ in range(6))
            
            # Проверяем, что такого кода еще нет в базе
            if not cls.objects.filter(short_code=short_code).exists():
                break
        
        # Создаем и сохраняем новую короткую ссылку
        short_link = cls.objects.create(
            original_url=original_url,
            short_code=short_code
        )
        
        return short_link
    
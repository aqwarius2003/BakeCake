from datetime import datetime
import requests
from urllib.parse import urlsplit

from django.utils import timezone
from .models import SettingsManager


def send_telegram_notification(order):
    """Отправляем уведомление в Telegram о новом заказе"""
    tg_bot_token, tg_chat_id = SettingsManager.get_telegram_settings()

    if not tg_bot_token or not tg_chat_id:
        print("Настройки Telegram не установлены. Уведомление не отправлено.")
        return

    delivery_datetime = timezone.make_aware(
        datetime.combine(order.delivery_date, order.delivery_time)
    )
    formatted_delivery_datetime = delivery_datetime.strftime("%d.%m.%Y %H:%M")

    message = (
        "🎂 *Новый заказ торта!*\n"
        f"🆔 Номер заказа: {order.id}\n"
        "👤 *Клиент:*\n"
        f"• Имя: {order.client.name}\n"
        f"• Телефон: {order.client.phone}\n"
        f"• Email: {order.client.email or 'нет'}\n\n"
        "📦 *Детали заказа:*\n"
        f"• Уровней: {order.cake.get_levels_display()}\n"
        f"• Форма: {order.cake.get_shape_display()}\n"
        f"• Топпинг: {order.cake.get_topping_display()}\n"
        f"• Адрес: {order.address}\n"
        f"• Комментарий: {order.comment or 'нет'}\n"
        f"📅 Дата и время доставки: {formatted_delivery_datetime}\n"
        f"💵 Сумма: {order.total_price} руб."
    )

    keyboard = {"inline_keyboard": []}

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{tg_bot_token}/sendMessage",
            json={
                "chat_id": tg_chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "reply_markup": keyboard,
            },
            timeout=5,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки в Telegram: {e}")


def get_vk_short_link(url):
    """Создает короткую ссылку через API ВКонтакте"""
    vk_token = SettingsManager.get_vk_token()
    if not vk_token:
        # Если токен VK не настроен, возвращаем оригинальный URL
        print("Токен ВКонтакте не настроен. Короткая ссылка не создана.")
        return url

    vk_api_url = 'https://api.vk.com/method/utils.getShortLink'
    payload = {
        'access_token': vk_token,
        'v': '5.199',
        'url': url
    }

    try:
        response = requests.get(vk_api_url, params=payload)
        response.raise_for_status()
        api_response = response.json()
        vk_short_url = api_response['response'].get('short_url')

        # Больше не сохраняем ссылку в БД здесь - это делается в админке
        return vk_short_url
    except Exception as e:
        print(f"Ошибка при создании короткой ссылки VK: {e}")
        # В случае ошибки возвращаем оригинальный URL
        return url


def is_vk_short_link(url):
    """Проверяет, является ли ссылка короткой ссылкой VK"""
    return urlsplit(url).netloc == 'vk.cc'


def count_vk_clicks(url):
    """Получает количество кликов по короткой ссылке VK"""
    vk_token = SettingsManager.get_vk_token()
    if not vk_token:
        print("Токен ВКонтакте не настроен. Статистика кликов не получена.")
        return 0
    # Проверяем, является ли ссылка уже короткой ссылкой VK
    if not is_vk_short_link(url):
        url = get_vk_short_link(url)

    vk_api_url = 'https://api.vk.com/method/utils.getLinkStats'
    short_link = urlsplit(url)
    key_short_link = short_link.path.split('/')[-1]

    payload = {
        'access_token': vk_token,
        'v': '5.199',
        'key': key_short_link,
        # 'interval': 'forever',
        'extended': 0
    }

    try:
        response = requests.get(vk_api_url, params=payload)
        response.raise_for_status()
        api_response = response.json()
        url_stats = api_response.get('response', {}).get('stats', [])
        return url_stats[0].get('views', 0) if url_stats else 0
    except Exception:
        print(f"Ошибка при получении статистики кликов для ссылки: {url}")
        return 0

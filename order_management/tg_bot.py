from datetime import datetime
import requests

from django.utils import timezone
from environs import Env

env = Env()
env.read_env()

tg_bot_token = env("TELEGRAM_BOT_TOKEN")
tg_chat_id = env("TELEGRAM_CHAT_ID", None)


def send_telegram_notification(order):
    if not tg_chat_id:
        print("TELEGRAM_CHAT_ID не установлен. Уведомление не отправлено.")
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

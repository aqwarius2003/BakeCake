# 🎂 Проект «BakeCake» 

<<<<<<< HEAD
![](https://i.postimg.cc/ZqynvnHQ/lines-torts.jpg)
=======
![](https://i.postimg.cc/Dz6xDQFg/1.jpg)![](https://i.postimg.cc/50tsMH2M/2.jpg)![](https://i.postimg.cc/Qtn0NXFK/3.jpg)![](https://i.postimg.cc/yxgnkwRQ/4topt.jpg)
>>>>>>> LK

## 📌 Описание проекта

BakeCake — это веб-сервис, разработанный для ценителей уникальных десертов. Сервис объединяет интуитивный интерфейс, широкие возможности кастомизации и оперативную коммуникацию, делая процесс заказа сладких сюрпризов простым и приятным для клиентов, а для кондитеров — прозрачным и организованным.

Здесь вы сможете:

* Выбрать готовый вариант из постоянно обновляемой коллекции тортов с разнообразными дизайнами и вкусовыми комбинациями.
* Создать авторский торт — использовать гибкий конструктор для подбора уровня, формы, начинки и декора, воплотив любую творческую идею.
* Персонализировать заказ — добавить поздравительную надпись (доступно как опция за дополнительную плату).
* Настроить доставку — выбрать удобные дату и временное окно, а также указать адрес в зоне покрытия сервиса.

Для администраторов:

* Автоматизированные оповещения — система мгновенно отправляет уведомления о новых заказах в Telegram, упрощая управление заявками.

![Ок](https://i.postimg.cc/XYwHKSzt/ok-zakaz.jpg)

![ТГ_чат](https://i.postimg.cc/qB554GKD/image.jpg)

## 📌 Установка

### 🛠 Предварительные требования

- Python 3.10 или выше
- СУБД по вашему выбору
- Виртуальное окружение (рекомендуется)

## 🚀 Запуск

1. 📌 **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/aqwarius2003/BakeCake
   ```
   
2. 📌 **Установите зависимости:**
   ```bash
   pip install -r requirements.txt   
   ```
   
3. 📌 **Настройка переменных окружения:**

**Создайте файл .env в корне проекта и добавьте необходимые переменные окружения:**

```bash
# Для Telegram бота:
TELEGRAM_BOT_TOKEN='Ваш telegram_bot_token'
TELEGRAM_CHAT_ID='chat_id'(Телеграм ID администратора (который будет получать уведомления о новом заказе))

# Для settings:
# Указывает, находится ли приложение в режиме отладки.В продакшене всегда должно быть False.Если DEBUG = True, приложение будет выводить подробные сообщения об ошибках и автоматически перезагружаться при изменении кода.
DEBUG = env.bool("DEBUG", True)

# Секретный ключ для обеспечения безопасности вашего приложения.Используется для шифрования данных и защиты сессий.
SECRET_KEY= env.str('SECRET_KEY')

# Список хостов, которые могут обслуживаться вашим приложением.
ALLOWED_HOSTS = env.list([".localhost", "'127.0.0.1", "[::1]"])
```

4. 📌 **Примените миграции:**

   ```bash
   python manage.py migrate   
   ```

5. 📌 **Создайте суперпользователя для работы с админ-панелью:**

   ```bash
   python manage.py createsuperuser   
   ```
6. 📌 **Запустите сервер:**

   ```bash
   python manage.py runserver   
   ```
 Теперь вы можете открыть приложение в браузере по [адресу](http://127.0.0.1:8000/)  
 
![Главная](https://i.postimg.cc/QNw0RdLR/image.jpg)

![Создание](https://i.postimg.cc/h4yHhBkr/sozdanie-torta.jpg)

![Каталог](https://i.postimg.cc/rF73C9FR/katalog.jpg)
 
 и зайти в [админку](http://127.0.0.1:8000/admin/) где можно просмотреть и отредактировать "Заказы", "Клиенты", "Торты".

![Админка](https://i.postimg.cc/RFPb37DF/image.jpg)


## ✅ Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org)

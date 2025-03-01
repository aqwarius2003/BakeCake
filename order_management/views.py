from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib import messages
from django.contrib.auth import logout
from datetime import datetime
import json
from functools import wraps

from .models import Cake, Order, Client


def require_client(redirect_url='index'):
    """
    Декоратор для проверки наличия client_id в сессии.
    Если client_id отсутствует, перенаправляет на указанный URL.
    
    Args:
        redirect_url: URL для перенаправления в случае отсутствия client_id
    
    Returns:
        Декоратор, который проверяет наличие client_id в сессии
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            client_id = request.session.get('client_id')
            if not client_id:
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_client_info(client_id):
    """
    Получает информацию о клиенте и его заказах из базы данных.
    
    Args:
        client_id: ID клиента
    
    Returns:
        Словарь с данными о клиенте, последним адресом и количеством активных заказов
        или None, если клиент не найден
    """
    try:
        client = Client.objects.get(pk=client_id)
        # Получаем заказы клиента
        orders = Order.objects.filter(client=client)
        active_orders = orders.exclude(status__in=['cancelled', 'delivered'])
        orders_count = active_orders.count()
        
        # Получаем последний адрес из заказов, если они есть
        last_address = ''
        if orders.exists():
            last_order = orders.latest('created_at')
            last_address = last_order.address
        
        return {
            'client': client,
            'last_address': last_address,
            'orders_count': orders_count
        }
    except Client.DoesNotExist:
        return None


def update_session_client_data(request, client, last_address='', orders_count=0):
    """
    Обновляет данные клиента в сессии.
    
    Args:
        request: HTTP request объект
        client: объект модели Client
        last_address: последний адрес доставки
        orders_count: количество активных заказов
    """
    client_data = {
        'name': client.name,
        'phone': client.phone,
        'email': client.email,
        'address': last_address
    }
    
    request.session['client_id'] = client.id
    request.session['client_data'] = client_data
    request.session['orders_count'] = orders_count
    request.session.modified = True
    
    return client_data


def ensure_client_session(request):
    """
    Проверяет и обновляет данные клиента в сессии.
    Если данные клиента отсутствуют в сессии, но есть client_id,
    функция получает данные из БД и обновляет сессию.
    
    Args:
        request: HTTP request объект
    
    Returns:
        Словарь с данными клиента или None, если клиент не найден
    """
    client_id = request.session.get('client_id')
    client_data = request.session.get('client_data')
    
    # Если в сессии есть данные клиента, используем их
    if client_data and client_id:
        orders_count = request.session.get('orders_count', 0)
        return {
            'client_data': client_data,
            'client_id': client_id,
            'orders_count': orders_count
        }
    
    # Если в сессии нет данных клиента, но есть client_id, получаем данные из БД
    if client_id and not client_data:
        client_info = get_client_info(client_id)
        if client_info:
            client = client_info['client']
            last_address = client_info['last_address']
            orders_count = client_info['orders_count']
            
            client_data = update_session_client_data(
                request, client, last_address, orders_count
            )
            
            return {
                'client_data': client_data,
                'client_id': client_id,
                'orders_count': orders_count
            }
        else:
            # Если клиент не найден, очищаем сессию
            if 'client_id' in request.session:
                del request.session['client_id']
            if 'client_data' in request.session:
                del request.session['client_data']
            if 'orders_count' in request.session:
                del request.session['orders_count']
            request.session.modified = True
            return None
    
    return None


@csrf_exempt
def index(request):
    """
    Главная страница сайта.
    Обрабатывает просмотр главной страницы и создание заказа через форму.
    """
    # Получаем данные клиента из сессии или БД
    session_data = ensure_client_session(request)
    client_id = request.session.get('client_id')
    client_data = None
    client = None
    orders_count = 0
    
    if session_data:
        client_id = session_data['client_id']
        orders_count = session_data['orders_count']
        
        try:
            client = Client.objects.get(pk=client_id)
            # Преобразуем данные в JSON для шаблона
            client_data = json.dumps(session_data['client_data'])
        except Client.DoesNotExist:
            if 'client_id' in request.session:
                del request.session['client_id']
            if 'client_data' in request.session:
                del request.session['client_data']
            if 'orders_count' in request.session:
                del request.session['orders_count']
            request.session.modified = True

    # Если данные получены из формы
    if request.method == 'GET' and len(request.GET) > 1:
        try:
            # Получаем данные из GET-параметров
            levels = int(request.GET.get('LEVELS', 1))
            shape = {
                1: 'circle',
                2: 'square',
                3: 'rectangle'
            }.get(int(request.GET.get('FORM', 1)), 'circle')

            topping = {
                1: 'none',
                2: 'white_sauce',
                3: 'caramel_syrup',
                4: 'maple_syrup',
                5: 'blueberry_syrup',
                6: 'milk_chocolate',
                7: 'strawberry_syrup'
            }.get(int(request.GET.get('TOPPING', 1)), 'none')

            # Создаем торт
            cake = Cake.objects.create(
                levels=levels,
                shape=shape,
                topping=topping,
                berries=int(request.GET.get('BERRIES', 0)) 
                        if int(request.GET.get('BERRIES', 0)) > 0 else None,
                decor=int(request.GET.get('DECOR', 0)) 
                      if int(request.GET.get('DECOR', 0)) > 0 else None,
                inscription=request.GET.get('WORDS', '')
            )

            # Создаем или получаем клиента
            client, created = Client.objects.update_or_create(
                phone=request.GET['PHONE'],
                defaults={
                    'name': request.GET['NAME'],
                    'email': request.GET.get('EMAIL', ''),
                }
            )

            # Преобразуем дату и время
            delivery_date = datetime.strptime(
                request.GET.get('DATE'), '%Y-%m-%d'
            ).date()
            delivery_time = datetime.strptime(
                request.GET.get('TIME'), '%H:%M'
            ).time()

            # Определяем, является ли заказ срочным
            is_urgent = (datetime.combine(delivery_date, delivery_time) 
                         - datetime.now()).total_seconds() < 24 * 3600

            # Создаем заказ с учетом срочности
            order = Order.objects.create(
                client=client,
                cake=cake,
                address=request.GET['ADDRESS'],
                comment=request.GET.get('DELIVCOMMENTS', ''),
                delivery_date=delivery_date,
                delivery_time=delivery_time,
                total_price=cake.get_price(is_urgent=is_urgent),
                status='new'
            )

            # Получаем актуальное количество заказов клиента
            client_info = get_client_info(client.id)
            if client_info:
                # Обновляем сессию с новыми данными
                update_session_client_data(
                    request,
                    client_info['client'],
                    request.GET['ADDRESS'],  # Используем адрес из текущего заказа
                    client_info['orders_count']
                )

            messages.success(
                request,
                f'Заказ №{order.id} успешно создан! '
                f'Мы свяжемся с вами в ближайшее время.'
            )
            return redirect('index')

        except Exception as e:
            messages.error(
                request,
                'Произошла ошибка при создании заказа. '
                'Пожалуйста, попробуйте снова.'
            )
            return redirect('index')

    return render(request, 'index.html', {
        'client_data': client_data,
        'client': client,  # Добавляем client в контекст
        'orders_count': orders_count  # Добавляем количество заказов
    })


@csrf_exempt
def register(request):
    """
    Регистрирует нового клиента или обновляет существующего по номеру телефона.
    """
    if request.method == 'POST':
        phone = request.POST.get('phone')
        # тут будет блок проверки на валидность номера телефона
        if not phone:
            messages.error(request, "Введите номер телефона.")
            return redirect('register')

        # Проверка, существует ли телефон в базе данных
        if not Client.objects.filter(phone=phone).exists():
            # Перенаправление в личный кабинет для ввода данных
            messages.info(request, "Введите свое имя и email.")
            return redirect('/lk/?edit=true')

        # Логика создания клиента, если телефон существует
        name = request.POST.get('name')
        client, created = Client.objects.update_or_create(
            phone=phone,
            defaults={
                'name': name,
            }
        )
        request.session['client_id'] = client.id
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


def logout_view(request):
    """
    Выполняет выход пользователя из системы и перенаправляет на главную страницу.
    """
    logout(request)
    return redirect('index')


@require_client()
def lk_order(request):
    """
    Страница с заказами клиента в личном кабинете.
    """
    client_id = request.session.get('client_id')
    
    client_info = get_client_info(client_id)
    if not client_info:
        return redirect('index')
    
    client = client_info['client']
    orders_count = client_info['orders_count']
    
    # Обновляем количество заказов в сессии
    request.session['orders_count'] = orders_count
    request.session.modified = True
    
    # Получаем все заказы, включая отмененные и доставленные для отображения
    orders = Order.objects.filter(client=client)

    return render(request, 'lk-order.html', {
        'client': client, 
        'orders': orders,
        'orders_count': orders_count
    })


@csrf_exempt
def request_code(request):
    """
    Обрабатывает запрос на отправку проверочного кода на телефон клиента.
    В текущей реализации код фиксирован (1234) и не отправляется реально.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone')
        # Здесь типу логика отправки СМС с кодом клиентский номер
        # Временный код
        code = '1234'
        request.session['verification_code'] = code
        request.session['phone_number'] = phone
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


@csrf_exempt
def verify_code(request):
    """
    Проверяет код верификации, полученный через SMS.
    Если код верный, создает клиента (если отсутствует) и обновляет сессию.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone')
        code = data.get('code')
        stored_code = request.session.get('verification_code')
        stored_phone = request.session.get('phone_number')

        if phone == stored_phone and code == stored_code:
            # Получаем или создаем клиента
            client, created = Client.objects.get_or_create(
                phone=phone,
                defaults={'name': '', 'email': ''}
            )
            
            # Получаем информацию о клиенте и его заказах
            client_info = get_client_info(client.id)
            
            # Обновляем сессию
            client_data = update_session_client_data(
                request,
                client,
                client_info['last_address'] if client_info else '',
                client_info['orders_count'] if client_info else 0
            )
            
            # Очищаем временные данные
            if 'verification_code' in request.session:
                del request.session['verification_code']
            if 'phone_number' in request.session:
                del request.session['phone_number']

            # Формируем ответ
            response_data = {
                'status': 'success',
                'redirect_url': '/lk/?edit=true' if created else '/lk_order/',
                'client_data': client_data  # Добавляем данные в ответ
            }
            
            return JsonResponse(response_data)
        
        return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})


@require_client()
def lk_view(request):
    """
    Страница личного кабинета клиента.
    """
    # Проверяем и обновляем данные в сессии
    session_data = ensure_client_session(request)
    if not session_data:
        return redirect('index')
    
    # Для рендеринга в шаблоне
    return render(request, 'lk.html', {
        'client_data': json.dumps(session_data['client_data']),
        'client': session_data['client_data'],  # Передаем словарь вместо объекта модели
        'orders_count': session_data['orders_count']
    })


@require_GET
def get_client_data(request):
    """
    API-метод для получения данных клиента по номеру телефона.
    """
    phone = request.GET.get('phone')
    client_data = {}
    
    try:
        client = Client.objects.get(phone=phone)
        try:
            last_order = Order.objects.filter(client=client).latest('created_at')
            address = last_order.address
        except Order.DoesNotExist:
            address = ''
            
        client_data = {
            'name': client.name,
            'phone': client.phone,
            'email': client.email,
            'address': address
        }
    except Client.DoesNotExist:
        pass
    
    return JsonResponse(client_data)


@csrf_exempt
@require_http_methods(["POST"])
def update_client_data(request):
    """
    Обновляет данные клиента и сохраняет изменения в БД и сессии.
    """
    client_id = request.session.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        client = Client.objects.get(pk=client_id)
        data = json.loads(request.body)
        
        # Обновляем поля клиента
        client.name = data.get('name', client.name)
        client.phone = data.get('phone', client.phone)
        client.email = data.get('email', client.email)
        client.save()

        # Получаем обновленную информацию о клиенте
        client_info = get_client_info(client_id)
        
        # Обновляем сессию
        update_session_client_data(
            request,
            client,
            client_info['last_address'],
            client_info['orders_count']
        )

        # Возвращаем JSON с указанием на перенаправление
        return JsonResponse({
            'status': 'success', 
            'redirect_url': '/lk_order/'
        })
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cake, Order, Client
from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_http_methods


@csrf_exempt
def index(request):
    # Проверяем, есть ли ID пользователя в сессии
    client_id = request.session.get('client_id')
    client_data = None
    if client_id:
        try:
            client = Client.objects.get(pk=client_id)
            client_data = {
                'name': client.name,
                'phone': client.phone,
                'email': client.email
            }
        except Client.DoesNotExist:
            # pass
            # удаляем из сессии пользвателя, если его не существует
            del request.session['client_id']

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
                inscription=request.GET.get('WORDS', '')
            )

            # Создаем или получаем клиента
            client, created = Client.objects.update_or_create(
                phone=request.GET['PHONE'],
                defaults={
                    'name': request.GET['NAME'],
                    'email': request.GET.get('EMAIL', '')
                }
            )

            # Преобразуем дату и время
            delivery_date = datetime.strptime(
                request.GET.get('DATE'), '%Y-%m-%d'
            ).date()
            delivery_time = datetime.strptime(
                request.GET.get('TIME'), '%H:%M'
            ).time()

            # Создаем заказ
            order = Order.objects.create(
                client=client,
                cake=cake,
                address=request.GET['ADDRESS'],
                comment=request.GET.get('DELIVCOMMENTS', ''),
                delivery_date=delivery_date,
                delivery_time=delivery_time,
                total_price=cake.get_price(),
                status='new'
            )
            # Сохраняем ID клиента в сессии
            request.session['client_id'] = client.id

            messages.success(
                request,
                f'Заказ №{order.id} успешно создан! Мы свяжемся с вами в ближайшее время.'
            )
            return redirect('index')

        except Exception as e:
            messages.error(
                request,
                'Произошла ошибка при создании заказа. Пожалуйста, попробуйте снова.'
            )
            return redirect('index')

    return render(request, 'index.html', {'client_data': client_data})


@csrf_exempt
def register(request):
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
    logout(request)
    return redirect('index')


def lk_order(request):
    client_id = request.session.get('client_id')
    if not client_id:
        return redirect('index')  # Если не авторизован, перенаправляем на главную

    try:
        client = Client.objects.get(pk=client_id)
        orders = Order.objects.filter(client=client)
    except Client.DoesNotExist:
        return redirect('index')

    return render(request, 'lk-order.html', {'client': client, 'orders': orders})


@csrf_exempt
def request_code(request):
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
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone')
        code = data.get('code')
        stored_code = request.session.get('verification_code')
        stored_phone = request.session.get('phone_number')

        if phone == stored_phone and code == stored_code:
            # Проверяем, существует ли клиент
            client, created = Client.objects.get_or_create(
                phone=phone,
                defaults={'name': '', 'email': ''}  # Устанавливаем имя и емейл пустыми только для новых клиентов
            )
            request.session['client_id'] = client.id
            # Очищаем сессионные переменные
            del request.session['verification_code']
            del request.session['phone_number']
            
            # Перенаправление в зависимости от того, новый клиент или нет
            if created:
                return JsonResponse({'status': 'success', 'redirect_url': '/lk/?edit=true'})
            else:
                return JsonResponse({'status': 'success', 'redirect_url': '/lk_order/'})
        else:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})


def lk_view(request):
    client_id = request.session.get('client_id')
    client = None
    if client_id:
        try:
            client = Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            return redirect('index')
    return render(request, 'lk.html', {'client': client})


@require_http_methods(["GET"])
def get_client_data(request):
    client_id = request.session.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        client = Client.objects.get(pk=client_id)
        return JsonResponse({'name': client.name, 'phone': client.phone, 'email': client.email})
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client not found'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def update_client_data(request):
    client_id = request.session.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        client = Client.objects.get(pk=client_id)
        data = json.loads(request.body)
        client.name = data.get('name', client.name)
        client.phone = data.get('phone', client.phone)
        client.email = data.get('email', client.email)
        client.save()

        # Обновляем данные в сессии
        request.session['client_name'] = client.name
        request.session['client_phone'] = client.phone
        request.session['client_email'] = client.email

        # Возвращаем JSON с указанием на перенаправление
        return JsonResponse({'status': 'success', 'redirect_url': '/lk_order/'})
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

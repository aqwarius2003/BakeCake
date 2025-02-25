from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cake, Order, Client
from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect


@csrf_exempt
def index(request):
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
            delivery_date = datetime.strptime(request.GET.get('DATE'), '%Y-%m-%d').date()
            delivery_time = datetime.strptime(request.GET.get('TIME'), '%H:%M').time()

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
            
            messages.success(request, f'Заказ №{order.id} успешно создан! Мы свяжемся с вами в ближайшее время.')
            return redirect('index')

        except Exception as e:
            messages.error(request, 'Произошла ошибка при создании заказа. Пожалуйста, попробуйте снова.')
            return redirect('index')

    return render(request, 'index.html')

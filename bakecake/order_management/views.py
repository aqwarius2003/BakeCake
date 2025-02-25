from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
from .models import Cake, Order, Client
from datetime import datetime
from rest_framework.response import Response


@csrf_exempt
def index(request):
    if request.method == 'GET' and request.GET:
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
            client, created = Client.objects.get_or_create(
                phone=request.GET.get('PHONE'),
                defaults={
                    'name': request.GET.get('NAME'),
                    'email': request.GET.get('EMAIL')
                }
            )

            # Если клиент существует, обновляем его данные
            if not created:
                client.name = request.GET.get('NAME')
                client.email = request.GET.get('EMAIL')
                client.save()

            # Преобразуем дату и время
            delivery_date = datetime.strptime(request.GET.get('DATE'), '%Y-%m-%d').date()
            delivery_time = datetime.strptime(request.GET.get('TIME'), '%H:%M').time()

            # Создаем заказ
            order = Order.objects.create(
                client=client,
                cake=cake,
                address=request.GET.get('ADDRESS'),
                comment=request.GET.get('DELIVCOMMENTS', ''),
                delivery_date=delivery_date,
                delivery_time=delivery_time,
                total_price=cake.get_price(),
                status='new'
            )
            return JsonResponse({
                'status': 'success',
                'order_id': order.id
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return render(request, 'index.html')




from django.contrib import admin
from django.urls import path
from order_management import views
from django.conf import settings
from django.conf.urls.static import static

print("STATIC_URL:", settings.STATIC_URL)
print("STATIC_ROOT:", settings.STATIC_ROOT)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    # path('create_order/', views.create_order, name='create_order'),
    # path('lk/', views.lk, name='lk'),
    # path('lk/orders/', views.lk_orders, name='lk_orders'),
    # path('update_profile/', views.update_profile, name='update_profile'),
    # path('auth/send_code/', views.send_code, name='send_code'),
    # path('auth/verify_code/', views.verify_code, name='verify_code'),   
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

print("Final urlpatterns:", urlpatterns)

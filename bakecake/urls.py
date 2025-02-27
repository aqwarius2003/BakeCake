from django.contrib import admin
from django.urls import path
from order_management import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('lk_order/', views.lk_order, name='lk_order'),
    path('request_code/', views.request_code, name='request_code'),
    path('verify_code/', views.verify_code, name='verify_code'),
    path('lk/', views.lk_view, name='lk'),
    path('api/client-data/',
         views.get_client_data, name='get_client_data'),
    path('api/update-client-data/',
         views.update_client_data, name='update_client_data'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

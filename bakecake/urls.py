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
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

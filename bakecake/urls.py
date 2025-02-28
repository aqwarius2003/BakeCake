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
    path('webhook/', views.telegram_webhook, name='telegram_webhook'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

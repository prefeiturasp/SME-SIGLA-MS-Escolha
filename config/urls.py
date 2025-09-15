from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def healthcheck(_request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('api/v1/', include('escolhas.urls')),
    path('admin/', admin.site.urls),
    path('', healthcheck, name='healthcheck'),

]

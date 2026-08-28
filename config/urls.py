from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),          # ← esta línea faltaba
    path('api/auth/', include('autenticacion.urls')),
    path('api/inventario/', include('inventario.urls')),
]
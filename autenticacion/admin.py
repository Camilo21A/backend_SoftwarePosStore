from django.contrib import admin
from .models import Tienda, Perfil

@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tienda')
    search_fields = ('usuario__username', 'tienda__nombre')
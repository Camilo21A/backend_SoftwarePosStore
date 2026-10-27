from django.contrib import admin
from .models import Venta, VentaItem

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display  = ('id_venta', 'fecha_hora', 'total', 'metodo_pago', 'estado', 'id_tienda')
    list_filter   = ('estado', 'metodo_pago', 'id_tienda')

@admin.register(VentaItem)
class VentaItemAdmin(admin.ModelAdmin):
    list_display = ('id_item', 'id_venta', 'id_producto', 'cantidad', 'subtotal')
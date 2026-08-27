from django.contrib import admin
from .models import Categoria, Producto, EntradaMercancia, EntradaItem

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display  = ('id_categoria', 'nombre', 'activo', 'id_tienda')
    list_filter   = ('activo', 'id_tienda')
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ('id_producto', 'nombre', 'precio_venta', 'stock_actual', 'activo', 'id_tienda')
    list_filter   = ('activo', 'id_tienda', 'id_categoria')
    search_fields = ('nombre', 'codigo_barras')

@admin.register(EntradaMercancia)
class EntradaMercanciaAdmin(admin.ModelAdmin):
    list_display  = ('id_entrada', 'fecha_hora', 'total', 'id_tienda')
    list_filter   = ('id_tienda',)

@admin.register(EntradaItem)
class EntradaItemAdmin(admin.ModelAdmin):
    list_display = ('id_item', 'id_entrada', 'id_producto', 'cantidad', 'costo_unit')
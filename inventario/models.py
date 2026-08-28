from django.db import models
from autenticacion.models import Tienda


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre       = models.CharField(max_length=100)
    activo       = models.BooleanField(default=True)
    id_tienda    = models.ForeignKey(Tienda, on_delete=models.CASCADE, db_column='id_tienda')

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id_producto   = models.AutoField(primary_key=True)
    nombre        = models.CharField(max_length=200)
    sinonimos     = models.JSONField(default=list, blank=True)  # ["pony", "pony malta"]
    codigo_barras = models.CharField(max_length=50, blank=True, null=True)
    precio_venta  = models.DecimalField(max_digits=12, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock_actual  = models.IntegerField(default=0)
    stock_minimo  = models.IntegerField(default=5)
    foto_url      = models.TextField(blank=True, null=True)
    activo        = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    id_categoria  = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_categoria')
    id_tienda     = models.ForeignKey(Tienda, on_delete=models.CASCADE, db_column='id_tienda')

    class Meta:
        db_table = 'productos'

    def __str__(self):
        return self.nombre


class EntradaMercancia(models.Model):
    id_entrada = models.AutoField(primary_key=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    total      = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notas      = models.TextField(blank=True, null=True)
    id_tienda  = models.ForeignKey(Tienda, on_delete=models.CASCADE, db_column='id_tienda')

    class Meta:
        db_table = 'entradas_mercancia'

    def __str__(self):
        return f'Entrada #{self.id_entrada} - {self.fecha_hora.date()}'


class EntradaItem(models.Model):
    id_item     = models.AutoField(primary_key=True)
    cantidad    = models.IntegerField()
    costo_unit  = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    id_entrada  = models.ForeignKey(EntradaMercancia, on_delete=models.CASCADE, db_column='id_entrada')
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')

    class Meta:
        db_table = 'entrada_items'

    def __str__(self):
        return f'{self.cantidad} x {self.id_producto.nombre}'
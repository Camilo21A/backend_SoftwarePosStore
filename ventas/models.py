from django.db import models
from autenticacion.models import Tienda
from inventario.models import Producto


class Venta(models.Model):

    METODOS_PAGO = [
        ('efectivo',      'Efectivo'),
        ('nequi',         'Nequi'),
        ('daviplata',     'Daviplata'),
        ('transferencia', 'Transferencia'),
        ('otro',          'Otro'),
    ]

    ESTADOS = [
        ('activa',  'Activa'),
        ('anulada', 'Anulada'),
    ]

    id_venta     = models.AutoField(primary_key=True)
    fecha_hora   = models.DateTimeField(auto_now_add=True)
    total        = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago  = models.CharField(max_length=20, choices=METODOS_PAGO)
    fue_por_voz  = models.BooleanField(default=False)
    estado       = models.CharField(max_length=10, choices=ESTADOS, default='activa')
    motivo_anulacion = models.TextField(blank=True, null=True)
    id_tienda    = models.ForeignKey(Tienda, on_delete=models.CASCADE, db_column='id_tienda')

    class Meta:
        db_table = 'ventas'

    def __str__(self):
        return f'Venta #{self.id_venta} — ${self.total}'


class VentaItem(models.Model):
    id_item         = models.AutoField(primary_key=True)
    cantidad        = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal        = models.DecimalField(max_digits=12, decimal_places=2)
    id_venta        = models.ForeignKey(Venta, on_delete=models.CASCADE, db_column='id_venta', related_name='items')
    id_producto     = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column='id_producto')

    class Meta:
        db_table = 'venta_items'

    def __str__(self):
        return f'{self.cantidad} x {self.id_producto.nombre}'
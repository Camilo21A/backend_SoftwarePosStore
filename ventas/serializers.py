from rest_framework import serializers
from .models import Venta, VentaItem
from inventario.models import Producto


class VentaItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='id_producto.nombre', read_only=True
    )
    id_producto     = serializers.IntegerField(source='id_producto_id')
    precio_unitario = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    subtotal        = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model  = VentaItem
        fields = ['id_item', 'id_producto', 'producto_nombre',
                  'cantidad', 'precio_unitario', 'subtotal']

class VentaSerializer(serializers.ModelSerializer):
    items = VentaItemSerializer(many=True)

    class Meta:
        model  = Venta
        fields = ['id_venta', 'fecha_hora', 'total', 'metodo_pago',
                  'fue_por_voz', 'estado', 'motivo_anulacion', 'items']
        read_only_fields = ['fecha_hora', 'estado']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        venta      = Venta.objects.create(**validated_data)

        total = 0
        for item in items_data:
            id_producto = item['id_producto_id']
            cantidad    = item['cantidad']
            producto    = Producto.objects.get(pk=id_producto)

            precio_unitario = producto.precio_venta
            subtotal        = precio_unitario * cantidad

            VentaItem.objects.create(
                id_venta        = venta,
                id_producto_id  = id_producto,
                cantidad        = cantidad,
                precio_unitario = precio_unitario,
                subtotal        = subtotal,
            )

            # Descuenta stock automáticamente (RF-03)
            producto.stock_actual -= cantidad
            producto.save()

            total += subtotal

        venta.total = total
        venta.save()
        return venta
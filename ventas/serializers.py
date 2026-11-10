from rest_framework import serializers
from .models import Venta, VentaItem
from inventario.models import Producto
from django.db import transaction

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
        def create(self, validated_data):
            items_data = validated_data.pop('items')
            tienda     = validated_data['id_tienda']

            if not items_data:
                raise serializers.ValidationError(
                    {'items': 'La venta debe tener al menos un producto.'}
                )

            # Si algo falla adentro, no se guarda nada (ni la venta ni el stock)
            with transaction.atomic():
                venta = Venta.objects.create(**validated_data)
                total = 0

                for item in items_data:
                    id_producto = item['id_producto_id']
                    cantidad    = item['cantidad']

                    if cantidad <= 0:
                        raise serializers.ValidationError(
                            {'items': 'La cantidad debe ser mayor a 0.'}
                        )

                    # Solo productos activos de ESTA tienda, bloqueados mientras se vende
                    try:
                        producto = Producto.objects.select_for_update().get(
                            pk=id_producto, id_tienda=tienda, activo=True
                        )
                    except Producto.DoesNotExist:
                        raise serializers.ValidationError(
                            {'items': f'El producto {id_producto} no existe.'}
                        )

                    if producto.stock_actual < cantidad:
                        raise serializers.ValidationError({
                            'items': f'Stock insuficiente de "{producto.nombre}": '
                                     f'hay {producto.stock_actual}.'
                        })

                    subtotal = producto.precio_venta * cantidad

                    VentaItem.objects.create(
                        id_venta        = venta,
                        id_producto     = producto,
                        cantidad        = cantidad,
                        precio_unitario = producto.precio_venta,
                        subtotal        = subtotal,
                    )

                    producto.stock_actual -= cantidad
                    producto.save()
                    total += subtotal

                venta.total = total
                venta.save()

            return venta
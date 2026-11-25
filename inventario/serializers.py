from django.db import transaction
from rest_framework import serializers
from .models import Categoria, Producto, EntradaMercancia, EntradaItem


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Categoria
        fields = ['id_categoria', 'nombre', 'activo']
        # id_tienda NO se expone — se asigna en la vista automáticamente


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(
        source='id_categoria.nombre', read_only=True
    )
    # Expone el ID numérico, no el objeto completo
    id_categoria = serializers.IntegerField(
        source='id_categoria_id', allow_null=True, required=False
    )

    class Meta:
        model  = Producto
        fields = [
            'id_producto', 'nombre', 'sinonimos', 'codigo_barras',
            'precio_venta', 'precio_compra', 'stock_actual', 'stock_minimo',
            'foto_url', 'activo', 'created_at',
            'id_categoria', 'categoria_nombre',
        ]
        read_only_fields = ['created_at']

    def create(self, validated_data):
        # Convierte id_categoria_id al campo correcto del modelo
        id_cat = validated_data.pop('id_categoria_id', None)
        producto = Producto(**validated_data)
        if id_cat is not None:
            producto.id_categoria_id = id_cat
        producto.save()
        return producto

    def update(self, instance, validated_data):
        id_cat = validated_data.pop('id_categoria_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if id_cat is not None:
            instance.id_categoria_id = id_cat
        instance.save()
        return instance


class EntradaItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='id_producto.nombre', read_only=True
    )
    id_producto = serializers.IntegerField(source='id_producto_id')
    cantidad    = serializers.IntegerField(min_value=1)

    class Meta:
        model  = EntradaItem
        fields = ['id_item', 'id_producto', 'producto_nombre',
                  'cantidad', 'costo_unit']


class EntradaMercanciaSerializer(serializers.ModelSerializer):
    items = EntradaItemSerializer(many=True, source='entradaitem_set')

    class Meta:
        model  = EntradaMercancia
        fields = ['id_entrada', 'fecha_hora', 'total', 'notas', 'items']
        read_only_fields = ['fecha_hora', 'total']

    def create(self, validated_data):
        items_data = validated_data.pop('entradaitem_set')
        tienda     = validated_data['id_tienda']

        if not items_data:
            raise serializers.ValidationError(
                {'items': 'La entrada debe tener al menos un producto.'}
            )

        # Todo o nada: si un producto falla, no se guarda nada
        with transaction.atomic():
            entrada = EntradaMercancia.objects.create(**validated_data)
            total = 0

            for item in items_data:
                try:
                    producto = Producto.objects.select_for_update().get(
                        pk=item['id_producto_id'],
                        id_tienda=tienda,
                        activo=True,
                    )
                except Producto.DoesNotExist:
                    raise serializers.ValidationError(
                        {'items': f'El producto {item["id_producto_id"]} no existe.'}
                    )

                cantidad = item['cantidad']
                costo = item.get('costo_unit')
                if costo is None:
                    costo = producto.precio_compra or 0

                EntradaItem.objects.create(
                    id_entrada  = entrada,
                    id_producto = producto,
                    cantidad    = cantidad,
                    costo_unit  = costo,
                )

                producto.stock_actual += cantidad
                producto.save()
                total += costo * cantidad

            entrada.total = total
            entrada.save()

        return entrada
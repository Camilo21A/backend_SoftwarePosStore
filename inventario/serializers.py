from rest_framework import serializers
from .models import Categoria, Producto, EntradaMercancia, EntradaItem


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Categoria
        fields = ['id_categoria', 'nombre', 'activo', 'id_tienda']
        read_only_fields = ['id_tienda']  # se asigna automáticamente desde el token


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(
        source='id_categoria.nombre', read_only=True
    )

    class Meta:
        model  = Producto
        fields = [
            'id_producto', 'nombre', 'sinonimos', 'codigo_barras',
            'precio_venta', 'precio_compra', 'stock_actual', 'stock_minimo',
            'foto_url', 'activo', 'created_at', 'id_categoria',
            'categoria_nombre', 'id_tienda'
        ]
        read_only_fields = ['id_tienda', 'created_at']


class EntradaItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='id_producto.nombre', read_only=True
    )

    class Meta:
        model  = EntradaItem
        fields = ['id_item', 'id_producto', 'producto_nombre', 'cantidad', 'costo_unit']


class EntradaMercanciaSerializer(serializers.ModelSerializer):
    items = EntradaItemSerializer(
        many=True,
        source='entradaitem_set'
    )

    class Meta:
        model  = EntradaMercancia
        fields = ['id_entrada', 'fecha_hora', 'total', 'notas', 'id_tienda', 'items']
        read_only_fields = ['id_tienda', 'fecha_hora']

    def create(self, validated_data):
        items_data = validated_data.pop('entradaitem_set')
        entrada    = EntradaMercancia.objects.create(**validated_data)

        for item in items_data:
            producto = item['id_producto']
            cantidad = item['cantidad']

            EntradaItem.objects.create(entrada=entrada, **item)

            # Actualiza el stock automáticamente (RF-03)
            producto.stock_actual += cantidad
            producto.save()

        # Calcula el total automáticamente
        entrada.total = sum(
            (i.get('costo_unit') or 0) * i['cantidad'] for i in items_data
        )
        entrada.save()

        return entrada
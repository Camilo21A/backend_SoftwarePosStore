from django.db import models
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

    class Meta:
        model  = EntradaItem
        fields = ['id_item', 'id_producto', 'producto_nombre', 'cantidad', 'costo_unit']


class EntradaMercanciaSerializer(serializers.ModelSerializer):
    items = EntradaItemSerializer(many=True, source='entradaitem_set')

    class Meta:
        model  = EntradaMercancia
        fields = ['id_entrada', 'fecha_hora', 'total', 'notas', 'items']
        read_only_fields = ['fecha_hora']

    def create(self, validated_data):
        items_data = validated_data.pop('entradaitem_set')
        entrada    = EntradaMercancia.objects.create(**validated_data)

        for item in items_data:
            id_producto = item['id_producto_id']
            cantidad    = item['cantidad']
            EntradaItem.objects.create(
                id_entrada=entrada,
                id_producto_id=id_producto,
                cantidad=cantidad,
                costo_unit=item.get('costo_unit'),
            )
            # Actualiza stock automáticamente (RF-03)
            Producto.objects.filter(pk=id_producto).update(
                stock_actual=models.F('stock_actual') + cantidad
            )

        entrada.total = sum(
            (i.get('costo_unit') or 0) * i['cantidad'] for i in items_data
        )
        entrada.save()
        return entrada
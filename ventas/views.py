from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Venta, VentaItem
from .serializers import VentaSerializer
from autenticacion.models import Perfil
from inventario.models import Producto


def get_tienda(request):
    perfil = Perfil.objects.filter(usuario=request.user).first()
    return perfil.tienda if perfil else None


class VentaListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = VentaSerializer

    def get_queryset(self):
        tienda = get_tienda(self.request)
        qs     = Venta.objects.filter(id_tienda=tienda).order_by('-fecha_hora')

        # Filtros opcionales
        estado      = self.request.query_params.get('estado')
        metodo_pago = self.request.query_params.get('metodo_pago')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        if estado:      qs = qs.filter(estado=estado)
        if metodo_pago: qs = qs.filter(metodo_pago=metodo_pago)
        if fecha_desde: qs = qs.filter(fecha_hora__date__gte=fecha_desde)
        if fecha_hasta: qs = qs.filter(fecha_hora__date__lte=fecha_hasta)

        return qs

    def perform_create(self, serializer):
        tienda = get_tienda(self.request)
        serializer.save(id_tienda=tienda)


class VentaDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = VentaSerializer

    def get_queryset(self):
        tienda = get_tienda(self.request)
        return Venta.objects.filter(id_tienda=tienda)


class AnularVentaView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        tienda = get_tienda(request)
        try:
            venta = Venta.objects.get(pk=pk, id_tienda=tienda)
        except Venta.DoesNotExist:
            return Response(
                {'error': 'Venta no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        if venta.estado == 'anulada':
            return Response(
                {'error': 'La venta ya está anulada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        motivo = request.data.get('motivo', '')
        if not motivo:
            return Response(
                {'error': 'Debe proporcionar un motivo de anulación'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Revierte el stock de cada item
        for item in venta.items.all():
            producto = item.id_producto
            producto.stock_actual += item.cantidad
            producto.save()

        venta.estado           = 'anulada'
        venta.motivo_anulacion = motivo
        venta.save()

        return Response(VentaSerializer(venta).data)


class StockBajoView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tienda    = get_tienda(request)
        productos = Producto.objects.filter(
            id_tienda=tienda,
            activo=True,
        ).extra(where=['stock_actual <= stock_minimo'])

        from inventario.serializers import ProductoSerializer
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Categoria, Producto, EntradaMercancia
from .serializers import (
    CategoriaSerializer, ProductoSerializer, EntradaMercanciaSerializer
)
from autenticacion.models import Perfil


def get_tienda(request):
    """Obtiene la tienda asociada al usuario autenticado."""
    perfil = Perfil.objects.filter(usuario=request.user).first()
    return perfil.tienda if perfil else None


# ─── CATEGORÍAS ───────────────────────────────────────────
class CategoriaListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = CategoriaSerializer

    def get_queryset(self):
        tienda = get_tienda(self.request)
        return Categoria.objects.filter(id_tienda=tienda, activo=True)

    def perform_create(self, serializer):
        tienda = get_tienda(self.request)
        serializer.save(id_tienda=tienda)


class CategoriaDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = CategoriaSerializer

    def get_queryset(self):
        tienda = get_tienda(self.request)
        return Categoria.objects.filter(id_tienda=tienda)


# ─── PRODUCTOS ────────────────────────────────────────────
class ProductoListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ProductoSerializer

    def get_queryset(self):
        tienda = get_tienda(self.request)
        qs     = Producto.objects.filter(id_tienda=tienda, activo=True)

        # Filtros opcionales por query params
        nombre   = self.request.query_params.get('nombre')
        categoria = self.request.query_params.get('categoria')
        barras   = self.request.query_params.get('codigo_barras')

        if nombre:
            qs = qs.filter(nombre__icontains=nombre)
        if categoria:
            qs = qs.filter(id_categoria=categoria)
        if barras:
            qs = qs.filter(codigo_barras=barras)

        return qs

    def perform_create(self, serializer):
        tienda = get_tienda(self.request)
        serializer.save(id_tienda=tienda)


class ProductoDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ProductoSerializer

    def get_queryset(self):
        tienda = get_tienda(self.request)
        return Producto.objects.filter(id_tienda=tienda)

    def perform_destroy(self, instance):
        # Archivar en vez de eliminar (RF-02)
        instance.activo = False
        instance.save()


# ─── ENTRADAS DE MERCANCÍA ────────────────────────────────
class EntradaMercanciaListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = EntradaMercanciaSerializer

    def get_queryset(self):
        tienda = get_tienda(self.request)
        return EntradaMercancia.objects.filter(id_tienda=tienda).order_by('-fecha_hora')

    def perform_create(self, serializer):
        tienda = get_tienda(self.request)
        serializer.save(id_tienda=tienda)
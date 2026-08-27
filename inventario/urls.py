from django.urls import path
from .views import (
    CategoriaListCreateView, CategoriaDetailView,
    ProductoListCreateView, ProductoDetailView,
    EntradaMercanciaListCreateView,
)

urlpatterns = [
    # Categorías
    path('categorias/',          CategoriaListCreateView.as_view()),
    path('categorias/<int:pk>/', CategoriaDetailView.as_view()),

    # Productos
    path('productos/',           ProductoListCreateView.as_view()),
    path('productos/<int:pk>/',  ProductoDetailView.as_view()),

    # Entradas de mercancía
    path('entradas/',            EntradaMercanciaListCreateView.as_view()),
]
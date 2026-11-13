from django.urls import path
from .views import (
    VentaListCreateView,
    VentaDetailView,
    AnularVentaView,
    StockBajoView,
)

urlpatterns = [
    path('',                  VentaListCreateView.as_view()),
    path('<int:pk>/',         VentaDetailView.as_view()),
    path('<int:pk>/anular/',  AnularVentaView.as_view()),
    path('stock-bajo/',       StockBajoView.as_view()),
]
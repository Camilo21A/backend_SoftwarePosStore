from django.urls import path
from .views import LoginView, LogoutView, TiendaListView, TiendaToggleActivaView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('tiendas/', TiendaListView.as_view(), name='tiendas-list'),
    path('tiendas/<int:pk>/toggle/', TiendaToggleActivaView.as_view(), name='tiendas-toggle'),
]
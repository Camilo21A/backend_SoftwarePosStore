from django.db import models
from django.contrib.auth.models import User

class Tienda(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    activa = models.BooleanField(default=True)
    fecha_aviso_desactivacion = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, null=True, blank=True)
    # tienda = None  →  este usuario es el admin (super-admin)

    def __str__(self):
        return self.usuario.username
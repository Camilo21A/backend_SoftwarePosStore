from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, TiendaSerializer
from .models import Perfil

class LoginView(APIView):
    permission_classes = []  # público

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if usuario is None:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        perfil = Perfil.objects.filter(usuario=usuario).first()

        # Si tiene tienda asociada, verificar que esté activa
        if perfil and perfil.tienda and not perfil.tienda.activa:
            return Response(
                {'error': 'Esta tienda está desactivada. Solo puede consultar registros.'},
                status=status.HTTP_403_FORBIDDEN
            )

        token, _ = Token.objects.get_or_create(user=usuario)

        return Response({
            'token': token.key,
            'es_admin': perfil is None or perfil.tienda is None,
            'tienda': TiendaSerializer(perfil.tienda).data if perfil and perfil.tienda else None,
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
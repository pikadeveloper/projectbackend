from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from .serializers import UserSerializer,AuthTokenSerializer, OfertaDeEmpleoSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from base.models import OfertaDeEmpleo
from rest_framework.permissions import IsAuthenticated


class UserDetail(generics.RetrieveDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

class UserList(generics.ListCreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Personaliza la respuesta
        return Response(
            {
                "success": True,
                "message": "Usuario registrado correctamente",
                "data": serializer.data,  # Devuelve los datos del usuario (excepto la contraseña)
            },
            status=status.HTTP_201_CREATED
        )
    
class LoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializers = self.serializer_class(data=request.data, context={'request':request})
        serializers.is_valid(raise_exception=True)
        user = serializers.validated_data['user']
        token,created = Token.objects.get_or_create(user=user)
        user.last_join = now()
        user.save()
        return Response({
            'token': token.key,
            'username': user.username,
            'user_id': user.id,
            'email': user.email,
            'firstname':user.firstname,
            'date_joined': user.date_joined,
            'last_join': user.last_join,
            'is_employer':user.is_employer,
        })


#Vistas de Empresa
class OfertaDeEmpleoList(generics.ListCreateAPIView):

    queryset = OfertaDeEmpleo.objects.all()
    serializer_class = OfertaDeEmpleoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Permite filtrar ofertas por varios parámetros"""
        queryset = OfertaDeEmpleo.objects.all()
        
        # Filtros opcionales
        categoria = self.request.query_params.get('categoria', None)
        ubicacion = self.request.query_params.get('ubicacion', None)
        estado = self.request.query_params.get('estado', None)
        
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        if ubicacion:
            queryset = queryset.filter(ubicacion=ubicacion)
        if estado:
            queryset = queryset.filter(estado=estado)
            
        return queryset

class OfertaDeEmpleoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = OfertaDeEmpleo.objects.all()
    serializer_class = OfertaDeEmpleoSerializer
    permission_classes = [IsAuthenticated]

class OfertaDeEmpleoEmpresa(generics.ListAPIView):
    serializer_class = OfertaDeEmpleoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Obtiene las ofertas de una empresa específica"""
        empresa_id = self.kwargs['empresa_id']
        return OfertaDeEmpleo.objects.filter(empresa_id=empresa_id)

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from base.models import OfertaDeEmpleo, Empresa
from .serializers import UserSerializer, AuthTokenSerializer, OfertaDeEmpleoSerializer, EmpresaSerializer


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
        return Response(
            {
                "success": True,
                "message": "Usuario registrado correctamente",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializers = self.serializer_class(data=request.data, context={'request': request})
        serializers.is_valid(raise_exception=True)
        user = serializers.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user.last_join = now()
        user.save()

        # Determinar si el usuario es empleador y tiene empresa
        has_empresa = False
        if user.is_employer:
            # Si user.empresa existe, es que tiene empresa asociada
            has_empresa = hasattr(user, 'empresa')

        return Response({
            'token': token.key,
            'username': user.username,
            'user_id': user.id,
            'email': user.email,
            'firstname': user.firstname,
            'date_joined': user.date_joined.isoformat(),
            'last_join': user.last_join.isoformat() if user.last_join else None,
            'is_employer': user.is_employer,
            'has_empresa': has_empresa
        })


class OfertaDeEmpleoList(generics.ListCreateAPIView):
    queryset = OfertaDeEmpleo.objects.all()
    serializer_class = OfertaDeEmpleoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = OfertaDeEmpleo.objects.all()
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
        empresa_id = self.kwargs['empresa_id']
        return OfertaDeEmpleo.objects.filter(empresa_id=empresa_id)


class RegisterEmployerAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        serializer.validated_data['is_employer'] = True
        serializer.save()


class CreateTokenAPIView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class IsEmployerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_employer)


class EmpresaCreateAPIView(generics.CreateAPIView):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployerUser]


class EmpresaDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployerUser]

    def get_object(self):
        return Empresa.objects.get(empresa=self.request.user)

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from base.models import Account, OfertaDeEmpleo, Empresa

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields =('email','password','firstname', 'date_joined', 'last_join','is_employer')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            'date_joined': {'read_only': True},
            'last_join': {'read_only': True}
        }

    def create(self, validate_data):
        user = Account(**validate_data)
        user.set_password(validate_data['password'])
        user.save()
        return user

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type':'password'},
        trim_whitespace = False
    )
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )
        if not user:
            raise serializers.ValidationError("Credenciales de Usuario Invalidas")
        attrs['user'] = user
        return attrs
    
class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = [
            'id', 'empresa', 'nombre', 'descripcion', 'ubicacion',
            'rut', 'razon_social', 'giro', 'sitio_web', 'telefono',
            'email_contacto', 'direccion_comercial', 'fecha_registro',
            'logo', 'is_active'
        ]
        read_only_fields = ['fecha_registro', 'empresa']
        
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("No se ha podido determinar el usuario o no está autenticado.")

        if not user.is_employer:
            raise serializers.ValidationError("El usuario no tiene permisos para crear una empresa.")

        empresa = Empresa.objects.create(empresa=user, **validated_data)
        return empresa

class OfertaDeEmpleoSerializer(serializers.ModelSerializer):
    empresa = EmpresaSerializer(read_only=True)

    class Meta:
        model = OfertaDeEmpleo
        fields = [
            'id',
            'empresa',  # detalle de la empresa
            'titulo_trabajo',
            'descripcion',
            'categoria',
            'ubicacion',
            'requisitos_especificos',
            'fecha_publicacion',
            'salario',
            'estado'
        ]
        read_only_fields = ['fecha_publicacion']
        
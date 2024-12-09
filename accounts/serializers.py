from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from base.models import Account, OfertaDeEmpleo, Empresa

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields =('email','password','firstname', 'date_joined', 'last_join','is_employer')
        extra_kwargs = {'password':{'write_only':True,'min_length':8}}

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
        fields = ['id', 'nombre', 'descripcion', 'ubicacion']

class OfertaDeEmpleoSerializer(serializers.ModelSerializer):
    empresa = EmpresaSerializer(source='empresa_id', read_only=True)  # Para obtener los detalles de la empresa
    
    class Meta:
        model = OfertaDeEmpleo
        fields = [
            'id',
            'empresa_id',
            'empresa',  # Incluye los detalles de la empresa
            'titulo_trabajo',
            'descripcion',
            'categoria',
            'ubicacion',
            'requisitos_especificos',
            'fecha_publicacion',
            'salario',
            'state',
            'estado'
        ]
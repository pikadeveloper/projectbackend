from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username=None, password=None):
        if not email:
            raise ValueError("Los usuarios deben tener una dirección de correo electrónico")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user_employer(self, email, username=None, password=None):
        user = self.create_user(email=email, username=username, password=password)
        user.is_employer = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None):
        user = self.create_user(email=email, username=username, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_join = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_employer = models.BooleanField(default=False)
    firstname = models.CharField(max_length=30, blank=True)
    lastname = models.CharField(max_length=60, blank=True)
    address1 = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)
    cellphone = models.CharField(max_length=12, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Si necesitas campos adicionales, agrégalos aquí

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'


# Modelo de empresa (versión refinada)
class Empresa(models.Model):
    empresa = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        related_name='empresa',
        limit_choices_to={'is_employer': True}
    )
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=255)
    rut = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=255)
    giro = models.CharField(max_length=255)
    sitio_web = models.URLField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20)
    email_contacto = models.EmailField(max_length=60)
    direccion_comercial = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to='empresas/logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'


class OfertaDeEmpleo(models.Model):
    ACTIVA = 'activa'
    DESACTIVADA = 'desactivada'
    ESTADOS = [
        (ACTIVA, 'Activa'),
        (DESACTIVADA, 'Desactivada')
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ofertas')
    titulo_trabajo = models.CharField(max_length=255)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    requisitos_especificos = models.TextField(blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    salario = models.IntegerField(blank=True, null=True)
    # Considera remover el booleano `state` si `estado` ya indica lo necesario
    estado = models.CharField(max_length=255, choices=ESTADOS, default=ACTIVA)

    class Meta:
        verbose_name = 'Oferta de Empleo'
        verbose_name_plural = 'Ofertas de Empleo'

    def __str__(self):
        return self.titulo_trabajo


class SolicitudDeEmpleo(models.Model):
    PENDIENTE = 'pendiente'
    APROBADO = 'aprobado'
    RECHAZADO = 'rechazado'
    ESTADOS_SOLICITUD = [
        (PENDIENTE, 'Pendiente'),
        (APROBADO, 'Aprobado'),
        (RECHAZADO, 'Rechazado'),
    ]

    usuario = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='solicitudes')
    oferta_empleo = models.ForeignKey(OfertaDeEmpleo, on_delete=models.CASCADE, related_name='solicitudes')
    estado = models.CharField(max_length=255, choices=ESTADOS_SOLICITUD, default=PENDIENTE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Solicitud de Empleo'
        verbose_name_plural = 'Solicitudes de Empleo'

    def __str__(self):
        return f"Solicitud de {self.usuario.email} a {self.oferta_empleo.titulo_trabajo}"


class ValoracionYComentarios(models.Model):
    usuario = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='valoraciones')
    oferta_empleo = models.ForeignKey(OfertaDeEmpleo, on_delete=models.CASCADE, related_name='valoraciones')
    comentario = models.TextField(blank=True)
    calificacion = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        verbose_name = 'Valoración y Comentario'
        verbose_name_plural = 'Valoraciones y Comentarios'

    def __str__(self):
        return f"Valoración de {self.usuario.email} a {self.oferta_empleo.titulo_trabajo}"

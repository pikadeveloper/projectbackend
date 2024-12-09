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
    #Funciones PARA PERMISOS
    def create_user(self, email, username=None, password=None):
        if not email:
            raise ValueError("Los usuarios deben tener una dirección de correo electrónico")
        user = self.model(username=username,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user_employer(self, email, username=None, password=None):
        if not email:
            raise ValueError("Los usuarios deben tener una dirección de correo electrónico")
        user = self.model(username=username,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_employer = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None):
        user = self.create_user(username=username,
            email=self.normalize_email(email),
            password = password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

#Clase CUENTA BASE
class Account(AbstractBaseUser, PermissionsMixin):
    email= models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True, null=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_join = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_employer = models.BooleanField(default=False)
    firstname = models.CharField(max_length=30, blank=True)
    lastname = models.CharField(max_length=60, blank=True)
    address1 = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)
    cellphone = models.CharField(max_length=12, blank=True)

    USERNAME_FIELD='email'

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    
        
# Modelo de empresa
class Empresa(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=255)

    # Modelo de oferta de empleo
class OfertaDeEmpleo(models.Model):
    id = models.AutoField(primary_key=True)
    empresa_id = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    titulo_trabajo = models.CharField(max_length=255)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    requisitos_especificos = models.TextField(blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    salario = models.IntegerField(blank=True, null=True)
    state = models.BooleanField()
    estado = models.CharField(max_length=255, choices=[('activa', 'Activa'), ('desactivada', 'Desactivada')])

# Modelo de solicitud de empleo
class SolicitudDeEmpleo(models.Model):
    id = models.AutoField(primary_key=True)
    usuario_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    oferta_empleo_id = models.ForeignKey(OfertaDeEmpleo, on_delete=models.CASCADE)
    estado = models.CharField(max_length=255, choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')])
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

# Modelo de valoración y comentario
class ValoracionYComentarios(models.Model):
    id = models.AutoField(primary_key=True)
    usuario_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    oferta_empleo_id = models.ForeignKey(OfertaDeEmpleo, on_delete=models.CASCADE)
    comentario = models.TextField(blank=True)
    calificacion = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])


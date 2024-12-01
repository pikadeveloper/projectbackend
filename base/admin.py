from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUser
from django.utils.translation import gettext as _

from base import models

class UserAdmin(BaseUser):
    ordering = ['id']
    list_display = ['id','email', 'username', 'firstname', 'lastname']
    list_display_links = ['id','email']
    fieldsets = (
        (None,{'fields':('username','email','password')}),
        (_('Información Personal'), {'fields':('firstname', 'lastname')}),
        (_('Permisos'),{'fields':('is_employer','is_active','is_staff','is_superuser')}),
        (_('Ultimo Inicio de sesión'),{'fields':('last_login',)})
    )

admin.site.register(models.Account,UserAdmin)

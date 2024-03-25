from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cuenta


class CuentaAdmin(UserAdmin):
    list_display = (
        "correo_electronico",
        "nombre",
        "apellido",
        "username",
        "inicio_acceso",
        "ultimo_acceso",
        "is_active",
        "is_admin",
    )

    ordering = ["correo_electronico"]  # Orden
    list_display_links = ("correo_electronico", "username")  # Campos con link
    readonly_fields = ("inicio_acceso", "ultimo_acceso")  # Campos solo lectura
    filter_horizontal = ()  # Filtro horizontal
    list_filter = ["is_active"]
    # list_filter = ["is_active", "is_superadmin"]
    search_fields = ["nombre", "correo_electronico"]  # Toma estos campos como busqueda
    fieldsets = ()


admin.site.register(Cuenta, CuentaAdmin)


# class AccountAdmin(UserAdmin):
#     list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
#     list_display_links = ('email', 'first_name', 'last_name')
#     readonly_fields = ('last_login', 'date_joined')
#     ordering = ('-date_joined',)

#     filter_horizontal = ()
#     list_filter = ()
#     fieldsets = ()

# admin.site.register(Account, AccountAdmin)

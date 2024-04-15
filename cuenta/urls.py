from django.urls import path, include
from . import views

urlpatterns = [
    path("registrarse/", views.registrarse, name="registrarse"),
    path('activar_cuenta/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),      
    path("inicio_sesion/", views.inicio_sesion, name="inicio_sesion"),
    path("cerrar_sesion/", views.cerrar_sesion, name="cerrar_sesion"),
    path("perfil/", views.perfil, name="perfil_usuario"),
    path("desactivar_cuenta/", views.desactivar_cuenta, name="desactivar_cuenta"),    
    path("recuperar_password/", views.recuperar_password, name="recuperar_password"),
    path(
        "cambiar_password/<uidb64>/<token>/",
        views.enlace_cambiar_pwd,
        name="enlace_cambiar_pwd",
    ),
    path(
        "restablecer_password/", views.restablecer_password, name="restablecer_password"
    ),
    
    # ? ADMIN
    path("admin/usuario/", views.listar_usuario, name="lista_usuario"),
    path("admin/perfil/", views.perfil_admin, name="perfil_admin"),


    # ? API
    path("api/v1/signup/", views.signup),
    path("api/v1/login/", views.login),
    path("api/v1/logout/", views.logout),    
    path("api/v2/logout/", views.logoutV2),

    # Perfil
    path("api/v1/profile/", views.perfil_api),
    path("api/v1/get_profile/", views.get_profile),
    path("api/v1/put_profile/", views.put_profile),
    
    path("api/v1/deactivate_account/", views.deactivate_account),   
    path("api/v1/recover_password/", views.recover_password),
    
]

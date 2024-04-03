from django.urls import path, include
from . import views

urlpatterns = [
    path("registrarse/", views.registrarse, name="registrarse"),
    path('activar_cuenta/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),      
    path("inicio_sesion/", views.inicio_sesion, name="inicio_sesion"),
    path("cerrar_sesion/", views.cerrar_sesion, name="cerrar_sesion"),
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
    
    # ? API
    path("api/v1/signup/", views.signup),
    path("api/v1/login/", views.login),
    # path("api/v1/logout/", views.logout),
    path("api/v2/logout/", views.logoutv2),
    path("api/v1/deactivate_account/", views.deactivate_account),

    path("api/v2/deactivate_account/", views.deactivate_accountV2),

    path("api/v1/recover_password/", views.recover_password),
    
]

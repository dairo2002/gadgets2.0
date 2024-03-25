from django.urls import path, include
from . import views

urlpatterns = [
    path("registrarse/", views.registrarse, name="registrarse"),
    path('activar_cuenta/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),      
    path("inicio_sesion/", views.inicio_sesion, name="inicio_sesion"),
    path("cerrar_sesion/", views.cerrar_sesion, name="cerrar_sesion"),
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
    # api/v1/login/
    path("api/signup/v1/", views.signupAPIView),
    path("api/login/v1/", views.loginAPIView),
    path("api/logout/v1/", views.logoutAPIView),
    path("api/recover_password/v1/", views.recover_password),
    
]

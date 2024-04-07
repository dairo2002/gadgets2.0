"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("administrador/", admin.site.urls),
    # Vista principal, inicio
    path("", views.index, name="index"),
    path("admin/dashboard/", views.dashboard, name="dashboard"),       

    path("tienda/", include("tienda.urls")),
    path("carrito/", include("carrito.urls")),
    path("cuenta/", include("cuenta.urls")),
    path("pedido/", include("pedido.urls")),
    
    # API
    path("api/list_product/v1/", views.listProductAPIView),
    # Footer
    path("sobre_nosotros/", views.sobre_nosotros, name='sobre_nosotros'),
    path("politicas_privacidad/", views.politicas_privacidad, name='politicas_privacidad'),
    path("metodo_de_pago/", views.metodo_pago, name='metodo_pago'),
    path("terminos_y_condiciones/", views.terminos_condiciones, name='terminos_condiciones'),
    path("manuales/", views.manuales, name='manuales'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

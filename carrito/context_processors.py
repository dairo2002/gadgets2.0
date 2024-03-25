from .views import _carrito_sesion
from .models import Carrito
from tienda.models import Producto
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
import locale, decimal
from .carrito import Cart


def mostrar_carrito(request):     
    cart = Cart(request)
    items, totalFormato = cart.obtener_producto() 
    contador = cart.__len__()
    return dict(articulo_carrito=items, total=totalFormato,  contador=contador)


def contar_productos(request):
    contar = 0
    # if "admin" in request.path:
    #     return {}
    # else:
    #     try:
    #         carrito_sesion = CarritoSesion.objects.filter(
    #             carrito_session=_carrito_sesion(request)
    #         )
    #         if request.user.is_authenticated:
    #             carrito_articulos = Carrito.objects.all().filter(usuario=request.user)
    #         else:
    #             carrito_articulos = Carrito.objects.all().filter(
    #                 carritoSesion=carrito_sesion[:1]
    #             )

    #         for articulo in carrito_articulos:
    #             contar += articulo.activo
    #     except Carrito.DoesNotExist:
    #         contar = 0

    return dict(contar_productos=contar)

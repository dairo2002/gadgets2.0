from .views import _carrito_sesion
from .models import Carrito
from tienda.models import Producto
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
import locale, decimal
from .carrito import Cart


# FUNCIONA
# def mostrar_carrito(request):     
#     cart = Cart(request)
#     items, totalFormato = cart.obtener_producto() 
#     contador = cart.__len__()
#     return dict(articulo_carrito=items, total=totalFormato,  contador=contador)


def mostrar_carrito(request):     
    cart = Cart(request)
    items, totalFormato = cart.obtener_producto() 
    contador = cart.__len__()
    return dict(articulo_carrito=items, total=totalFormato,  contador=contador)
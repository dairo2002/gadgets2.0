from django.http import JsonResponse
from .views import _carrito_sesion
from .models import Carrito
from tienda.models import Producto
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .carrito import Cart


def mostrar_carrito(request):   
    cart = Cart(request)   
    items, totalFormato = cart.obtener_producto()
    contador = cart.__len__()
    return dict(articulo_carrito=items, total=totalFormato,  contador=contador)


# def mostrar_carrito(request):
#     cart = Cart(request)
#     items, totalFormato = cart.obtener_producto()
#     contador = cart.__len__()

#     carrito = []
#     for item in items:
#         carrito.append(
#             {
#                 "producto": item["producto"].nombre,
#                 "cantidad": item["cantidad"],
#                 "subtotal": item["subTotalFormato"],
#             }
#         )

#     data = {"articulo_carrito": carrito, "total": totalFormato, "contador": contador}

#     return JsonResponse(data)

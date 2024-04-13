from django.http import JsonResponse
from .models import Carrito, ItemCarrito
from tienda.models import Producto
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

import pdb

# pdb.set_trace()

from django.http import JsonResponse


def mostrar_carrito(request):
    cartitem = []
    subtotal = 0
    total = 0
    contador = 0

    try:
        if request.user.is_authenticated:
            cart = Carrito.objects.get(usuario=request.user, completed=False)
        elif "nonuser" in request.session:
            cart = Carrito.objects.get(session_id=request.session["nonuser"], completed=False)
        else:
            cart = None

        if cart:
            cartitem = cart.cartitems.all()
            for articulo in cartitem:
                if articulo.producto.aplicar_descuento:
                    descuento = articulo.producto.aplicar_descuento()
                    cantidad = articulo.cantidad
                    subtotal += descuento * cantidad
                else:
                    precio = articulo.producto.precio
                    cantidad = articulo.cantidad
                    subtotal += precio * cantidad

            total = subtotal
            contador = len(cartitem)

    except Carrito.DoesNotExist:
        pass

    subtotal_formato = "{:,.0f}".format(subtotal).replace(",", ".")
    total_formato = "{:,.0f}".format(total).replace(",", ".")

    return {
        'articulo_carrito': cartitem,
        'subtotal': subtotal_formato,
        'total': total_formato,
        'contador': contador,
    }


'''def mostrar_carrito(request):
    cartitem = []
    descuento = 0
    subtotal = 0
    cantidad = 0
    contador = 0
    total = 0
    cart = None
    try:
        if request.user.is_authenticated:
            #hay elemenntos en el noneuser
            #si los hay agregarlos al carrito del usuario autenticado
            #mostrar los productos del usuario con el noneuser
            # cartNoneUser = Carrito.objects.get(
            #     session_id=request.session["nonuser"], completed=False)
            
            # itemNoneUser = ItemCarrito.objects.filter(carrito=cartNoneUser)
            # print(itemNoneUser)
            # if itemNoneUser:
                cart = Carrito.objects.get(usuario=request.user, completed=False)
                item = ItemCarrito.objects.filter(carrito=cart)
                for articulo in item:
                    if articulo.producto.aplicar_descuento:
                        descuento = articulo.producto.aplicar_descuento()
                        cantidad = articulo.cantidad
                        subtotal = descuento * cantidad
                        total += subtotal
                    else:
                        precio = articulo.producto.precio
                        cantidad = articulo.cantidad
                        subtotal = precio * cantidad
                        total += subtotal
        else:
            cart = Carrito.objects.get(
                session_id=request.session["nonuser"], completed=False
            )
            item = ItemCarrito.objects.filter(carrito=cart)
            for articulo in item:
                if articulo.producto.aplicar_descuento:
                    descuento = articulo.producto.aplicar_descuento()
                    cantidad = articulo.cantidad
                    subtotal = descuento * cantidad
                    total += subtotal
                else:
                    precio = articulo.producto.precio
                    cantidad = articulo.cantidad
                    subtotal = precio * cantidad
                    total += subtotal
                
        # cartitems =  related_name="cartitems"
        cartitem = cart.cartitems.all()        
        
        # Utilizamos este metodo count() para contar cuantos objetos ahi en el carrito
        # contador = cartitem.count()
    except Exception as e:
        pass
        # print(e)

    subtotalFormato = "{:,.0f}".format(subtotal).replace(",", ".")
    totalFormato = "{:,.0f}".format(total).replace(",", ".")
    return dict(
        articulo_carrito=cartitem,
        subtotal=subtotalFormato,
        total=totalFormato,
        contador=len(cartitem),
    )

# def mostrar_carrito(request):
#     cartitem = []
#     descuento = 0
#     subtotal = 0
#     cantidad = 0
#     contador = 0
#     total = 0
#     cart = None

#     # data = json.loads(request.body)
#     try:
#         if request.user.is_authenticated:
#             cart = Carrito.objects.get(usuario=request.user, completed=False)
#         else:
#             cart = Carrito.objects.get(
#                 session_id=request.session["nonuser"], completed=False
#             )

#         item = ItemCarrito.objects.filter(carrito=cart)
#         for articulo in item:
#             if articulo.producto.aplicar_descuento:
#                 descuento = articulo.producto.aplicar_descuento()
#                 cantidad = articulo.cantidad
#                 subtotal = descuento * cantidad
#                 total += subtotal
#             else:
#                 precio = articulo.producto.precio
#                 cantidad = articulo.cantidad
#                 subtotal = precio * cantidad
#                 total += subtotal

#             cartitem.append(
#                 {
#                     "producto": articulo.producto.nombre,
#                     "imagen": articulo.producto.imagen.url,
#                     "cantidad": cantidad,
#                 }
#             )

#         # cartitem = list(cart.cartitems.all())
#         contador = len(cartitem)
#     except Exception as e:
#         print(e)

#     subtotalFormato = "{:,.0f}".format(subtotal).replace(",", ".")
#     totalFormato = "{:,.0f}".format(total).replace(",", ".")   

#     return dict(
#         articulo_carrito=cartitem,
#         subtotal=subtotalFormato,
#         total=totalFormato,
#         contador=contador,
#     )
'''
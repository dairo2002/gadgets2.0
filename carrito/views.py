import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from tienda.models import Producto
from .models import Carrito, ItemCarrito
from django.urls import resolve
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import pdb


@login_required(login_url="inicio_sesion")
def mostrar_carrito(request):
    # la Funcionalidad esta en el context_proccesor, nos permiter visualizar los productos donde queremos
    return render(request, "client/tienda/carrito.html")


# @login_required(login_url="inicio_sesion")
def add(request):
    data = json.loads(request.body)
    producto_id = data['id']
    #  data['id']
    producto = Producto.objects.get(id=producto_id)
    print(producto)
    if request.user.is_authenticated:
        cart, created = Carrito.objects.get_or_create(
            usuario=request.user, completed=False
        )
        cartitem, created = ItemCarrito.objects.get_or_create(
            carrito=cart, producto=producto
        )
        cartitem.cantidad += 1
        cartitem.save()
        print("add ",cart)
    return JsonResponse("Muy bien", safe=False)


# def add(request, producto_id):
#     cart = Cart(request)
#     if request.method == "POST":
#         cantidad_str = request.POST.get("txtCantidad")
#         if cantidad_str is not None and cantidad_str.isdigit():
#             cantidad = int(cantidad_str)
#             if cantidad > 0:
#                 producto = get_object_or_404(Producto, pk=producto_id)
#                 if producto.stock >= cantidad:
#                     cart.add(producto=producto, cantidad=cantidad)
#                     print("cantidad add ", cantidad)
#                     print("producto add ", producto)
#                 else:
#                     messages.error(
#                         request, "La cantidad solicitada excede el stock disponible"
#                     )
#             else:
#                 messages.error(request, "La cantidad debe ser mayor que 0")
#         else:
#             messages.error(request, "La cantidad no es un número válido")
#     return redirect("mostrar_carrito")

# def update(request, producto_id):
#     cart = Cart(request)
#     if request.method == "POST":
#         cantidad_str = request.POST.get("txtCantidad")
#         if cantidad_str is not None and cantidad_str.isdigit():
#             cantidad = int(cantidad_str)
#             if cantidad > 0:
#                 producto = get_object_or_404(Producto, pk=producto_id)
#                 if producto.stock >= cantidad:
#                     cart.update(producto=producto, cantidad=cantidad)
#                     # pdb.set_trace()
#                     print("cantidad Actualizar ", cantidad)
#                     print("producto Actualizar ", producto)
#                 else:
#                     messages.error(
#                         request, "La cantidad solicitada excede el stock disponible"
#                     )
#             else:
#                 messages.error(request, "La cantidad debe ser mayor que 0")
#         else:
#             messages.error(request, "La cantidad no es un número válido")
#     return redirect("mostrar_carrito")


def update(request):
    # JsonResponse toma un diccionario como argumento y lo convierte en una cadena JSON.
    # La cadena JSON se envía al cliente como respuesta HTTP.
    if request.method == "POST":
        # Obtiene los datos enviados en la solicitud POST
        product_id = request.POST.get("producto_id")
        quantity = request.POST.get("cantidad")
        # Verifica si los datos son válidos
        if product_id is not None and quantity is not None:
            # Actualiza las cantidades de los productos en el carrito
            # Devuelve una respuesta JSON indicando éxito
            return JsonResponse({"success": True})
        else:
            # Si falta algún dato, devuelve un mensaje de error
            return JsonResponse({"success": False, "error": "Faltan datos"})
    else:
        # Si no es una solicitud POST, devuelve un mensaje de error
        return JsonResponse({"success": False, "error": "Solicitud no válida"})


# Eliminar un producto por la cantidad
def delete_cantidad_carrito(request, producto_id, carrito_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    try:
        if request.user.is_authenticated:
            carrito = Carrito.objects.get(
                producto=producto, usuario=request.user, id=carrito_id
            )
        else:
            carrito = Carrito.objects.get(producto=producto, id=carrito_id)
        #  Actualización de la cantidad del carrito
        if carrito.cantidad > 1:
            # Si la cantidad es mayor que 1, se disminuye en 1 y se guarda
            carrito.cantidad -= 1
            carrito.save()
        else:
            # Eliminación del producto del carrito si la cantidad es 1 o menos
            carrito.delete()
    except:
        pass
    return redirect("mostrar_carrito")


def delete_producto_carrito(request, producto_id, carrito_id):
    producto = get_object_or_404(Producto, pk=producto_id)

    if request.user.is_authenticated:
        carrito = Carrito.objects.get(
            producto=producto, usuario=request.user, id=carrito_id
        )
    else:
        carrito = Carrito.objects.get(producto=producto, id=carrito_id)
    carrito.delete()
    return redirect("mostrar_carrito")

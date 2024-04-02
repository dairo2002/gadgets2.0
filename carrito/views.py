from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from tienda.models import Producto
from .models import Carrito, ItemCarrito
from django.urls import resolve
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import json
import uuid
import pdb


@login_required(login_url="inicio_sesion")
def mostrar_carrito(request):
    # la Funcionalidad esta en el context_proccesor, nos permiter visualizar los productos donde queremos
    return render(request, "client/tienda/carrito.html")


# @login_required(login_url="inicio_sesion")
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
#                     "id": articulo.id,
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

#     data = {
#         "articulo_carrito": cartitem,
#         "subtotal": subtotalFormato,
#         "total": totalFormato,
#         "contador": contador,
#     }

#     print(data)
#     return JsonResponse({'data': data})

# ? validar stock
def add(request):
    data = json.loads(request.body)
    # producto_id = data["id"]
    producto_id = data.get("id")
    producto = Producto.objects.get(id=producto_id)
    if producto.stock >= 1:                
        if request.user.is_authenticated:
            cart, created = Carrito.objects.get_or_create(
                usuario=request.user, completed=False
            )
            cartitem, created = ItemCarrito.objects.get_or_create(
                carrito=cart, producto=producto
            )
            cartitem.cantidad += 1
            cartitem.save()        
            # contador = cart.count()
        else:
            try:
                # Bloque en el cual se comprueba si ya hay una session
                cart = Carrito.objects.get(
                    session_id=request.session["nonuser"], completed=False
                )
            except:
                request.session["nonuser"] = str(uuid.uuid4())
                cart = Carrito.objects.create(
                    session_id=request.session["nonuser"], completed=False
                )
            cartitem, created = ItemCarrito.objects.get_or_create(
                carrito=cart, producto=producto
            )
            cartitem.cantidad += 1
            cartitem.save()
    else:
        messages.info(request, 'Lo siento, la cantidad solicitada excede el stock disponible')
        # return JsonResponse({"redirect": "/carrito/"})    

        # contador = cart.count()
    return JsonResponse({"redirect": "/carrito/"})



def updates(request):
    data = json.loads(request.body)
    producto_id = data["id"]
    nueva_cantidad = int(data["cantidad"])
    
    producto = Producto.objects.get(id=producto_id)
    
    if request.user.is_authenticated:
        cart, created = Carrito.objects.get_or_create(
            usuario=request.user, completed=False
        )
    else:
        try:
            cart = Carrito.objects.get(
                session_id=request.session["nonuser"], completed=False
            )
        except Carrito.DoesNotExist:
            request.session["nonuser"] = str(uuid.uuid4())
            cart = Carrito.objects.create(
                session_id=request.session["nonuser"], completed=False
            )

    try:
        cartitem = ItemCarrito.objects.get(carrito=cart, producto=producto)        
        if nueva_cantidad == 0:
            cartitem.delete()
        else:
            cartitem.cantidad = nueva_cantidad
            cartitem.save()
    except ItemCarrito.DoesNotExist:
        pass
        # Si el producto no está en el carrito, podemos decidir si crear un nuevo
        # item en el carrito con la cantidad proporcionada, o simplemente ignorar la solicitud.
    return JsonResponse({"redirect": "/carrito/"})


# def delete(request):
#     data = json.loads(request.body)
#     # print(request.body)
#     producto_id = data.get("id")
#     print("data ",data)
#     print("id producto ", producto_id)
#     producto = Producto.objects.get(id=producto_id)

#     print("producto ",producto)
#     if request.user.is_authenticated:
#         cart, _ = Carrito.objects.get_or_create(usuario=request.user, completed=False)
#     else:
#         cart_id = request.session.get("nonuser")
#         if not cart_id:
#             print(cart_id)
#             return JsonResponse({"error": "El carrito no existe"})

#         cart, _ = Carrito.objects.get_or_create(session_id=cart_id, completed=False)
#     try:
#         # pdb.set_trace()
#         cartitem = ItemCarrito.objects.get(carrito=cart, producto=producto)
#         cartitem.delete()
#     except ItemCarrito.DoesNotExist:
#         return JsonResponse({"error": "El producto no está en el carrito"})

#     return JsonResponse({"message": "Producto eliminado del carrito"}, safe=False)



def delete(request):
    data = json.loads(request.body)
    producto_id = data.get("id")
    if not producto_id:
        return JsonResponse({"error": "ID del producto no proporcionado"})
    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"})
    if request.user.is_authenticated:
        cart, _ = Carrito.objects.get_or_create(usuario=request.user, completed=False)
    else:
        cart_id = request.session.get("nonuser")
        if not cart_id:
            return JsonResponse({"error": "El carrito no existe"})
        cart, _ = Carrito.objects.get_or_create(session_id=cart_id, completed=False)
    try:
        cartitem = ItemCarrito.objects.get(carrito=cart, producto=producto)
        cartitem.delete()
        return JsonResponse({"redirect": "/carrito/"})        
    except ItemCarrito.DoesNotExist:
        return JsonResponse({"redirect": "/carrito/"})    
        







@api_view(["POST"])
def addAPI(request):
    # Corregir data.get("id") a  data["id"]
    data = json.loads(request.body)
    #  data["id"]
    producto_id = data.get(
        "id"
    )  # Usamos .get() para evitar KeyError si 'id' no está presente en el JSON
    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return Response(
            {"error": "Producto no encontrado"}, status=status.HTTP_400_BAD_REQUEST
        )

    if request.user.is_authenticated:
        cart, created = Carrito.objects.get_or_create(
            usuario=request.user, completed=False
        )
    else:
        session_id = request.session.get("nonuser") or str(uuid.uuid4())
        request.session["nonuser"] = session_id
        cart, created = Carrito.objects.get_or_create(
            session_id=session_id, completed=False
        )

    cart_item, created = ItemCarrito.objects.get_or_create(
        carrito=cart, producto=producto
    )
    cart_item.cantidad += 1
    cart_item.save()

    return Response(
        {"message": "Producto agregado al carrito correctamente"},
        status=status.HTTP_200_OK,
    )


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

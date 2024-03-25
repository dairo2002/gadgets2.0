from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from tienda.models import Producto
from .models import Carrito
from django.urls import resolve
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from carrito.carrito import Cart
import pdb


def _carrito_sesion(request):
    # Obtener la clave de sesión actual del usuario
    carrito = request.session.session_key
    # Verificar si el usuario tiene una sesión activa (si carrito es nulo o vacío)
    if not carrito:
        # Si no hay una sesión activa, crear una nueva sesión y obtener su clave
        carrito = request.session.create()
        # Devolver la clave de sesión (puede ser la existente o la recién creada)
    return carrito

@login_required(login_url="inicio_sesion")
def mostrar_carrito(request):
    # Renderizamos la pagina, para dar una ruta
    # la Funcionalidad esta en el context_proccesor
    # Al esta en el context_proccesor nos permite visualizar los productos de carrito en varias vistas
    return render(request, "client/tienda/carrito.html")


def add(request, producto_id):
    cart = Cart(request)
    if request.method == "POST":
        cantidad_str = request.POST.get("txtCantidad")
        if cantidad_str is not None and cantidad_str.isdigit():
            cantidad = int(cantidad_str)
            if cantidad > 0:
                producto = get_object_or_404(Producto, pk=producto_id)
                if producto.stock >= cantidad:
                    cart.add(producto=producto, cantidad=cantidad)                   
                    print("cantidad add ", cantidad)
                    print("producto add ", producto)
                else:
                    messages.error(
                        request, "La cantidad solicitada excede el stock disponible"
                    )
            else:
                messages.error(request, "La cantidad debe ser mayor que 0")
        else:
            messages.error(request, "La cantidad no es un número válido")
    return redirect("mostrar_carrito")


def update(request, producto_id):
    cart = Cart(request)
    if request.method == "POST":
        cantidad_str = request.POST.get("txtCantidad")
        if cantidad_str is not None and cantidad_str.isdigit():
            cantidad = int(cantidad_str)
            if cantidad > 0:
                producto = get_object_or_404(Producto, pk=producto_id)
                if producto.stock >= cantidad:
                    cart.update(producto=producto, cantidad=cantidad)
                    # pdb.set_trace()                                       
                    print("cantidad Actualizar ", cantidad)
                    print("producto Actualizar ", producto)
                else:
                    messages.error(
                        request, "La cantidad solicitada excede el stock disponible"
                    )
            else:
                messages.error(request, "La cantidad debe ser mayor que 0")
        else:
            messages.error(request, "La cantidad no es un número válido")
    return redirect("mostrar_carrito")




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

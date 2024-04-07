from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import CarritoSerializer, ItemCarritoSerializer
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from tienda.models import Producto
from .models import Carrito, ItemCarrito
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import json
import uuid
import pdb


@login_required(login_url="inicio_sesion")
def mostrar_carrito(request):
    # la Funcionalidad esta en el context_proccesor, nos permiter visualizar los productos donde queremos
    return render(request, "client/tienda/carrito.html")

def add(request):
    data = json.loads(request.body)
    producto_id = data.get("id")

    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({"redirect": "/carrito/"})

    # Verificar si el producto está en stock
    # if producto.stock <= 0:
    #     return JsonResponse({"redirect": "/carrito/"})

    if request.user.is_authenticated:
        # Manejar usuarios autenticados
        cart, created = Carrito.objects.get_or_create(usuario=request.user, completed=False)
        try:
            cartitem = ItemCarrito.objects.get(carrito=cart, producto=producto)
            if cartitem.cantidad < producto.stock:
                cartitem.cantidad += 1
                cartitem.save()
            else:
                # Mensaje de error si la cantidad excede el stock disponible
                return JsonResponse({"redirect": "/carrito/"})
        except ItemCarrito.DoesNotExist:
            if producto.stock > 0:
                cartitem = ItemCarrito.objects.create(carrito=cart, producto=producto)
            else:
                return JsonResponse({"redirect": "/carrito/"})

    else:
        # Manejar usuarios no autenticados con sesión
        session_id = request.session.get("nonuser")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["nonuser"] = session_id
        cart, created = Carrito.objects.get_or_create(session_id=session_id, completed=False)
        try:
            cartitem = ItemCarrito.objects.get(carrito=cart, producto=producto)
            if cartitem.cantidad < producto.stock:
                cartitem.cantidad += 1
                cartitem.save()
            else:                
                return JsonResponse({"redirect": "/carrito/"})
        except ItemCarrito.DoesNotExist:
            if producto.stock > 0:
                cartitem = ItemCarrito.objects.create(carrito=cart, producto=producto)
            else:
                return JsonResponse({"redirect": "/carrito/"})
    return JsonResponse({"redirect": "/carrito/"})


def updates(request):
    data = json.loads(request.body)
    producto_id = data.get("id")
    cantidad_str = data.get("cantidad")
    producto = Producto.objects.get(id=producto_id)
    
    try:
        nueva_cantidad = int(cantidad_str)
        if nueva_cantidad < 0:            
            return JsonResponse({"redirect": "/carrito/"})
        if producto.stock < nueva_cantidad:
            return JsonResponse({"redirect": "/carrito/"})
    except:
        return JsonResponse({"redirect": "/carrito/"})
    
  
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
    return JsonResponse({"redirect": "/carrito/"})


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
        

# ? API
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mostrar_carritoAPI(request):
    try:
        cart = None
        subtotal = 0
        total = 0

        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            cart = Carrito.objects.get(usuario=request.user, completed=False)
        else:
            # Si no está autenticado, buscar el carrito por el ID de sesión
            cart = Carrito.objects.get(session_id=request.session["nonuser"], completed=False)

        # Obtener los elementos del carrito asociados al carrito encontrado
        cartitems = ItemCarrito.objects.filter(carrito=cart)

        # Calcular el subtotal y el total
        for articulo in cartitems:
            if articulo.producto.aplicar_descuento:
                # Calcular el precio con descuento si está disponible
                descuento = articulo.producto.aplicar_descuento()
                cantidad = articulo.cantidad
                subtotal += descuento * cantidad
            else:
                # Si no hay descuento, calcular el subtotal con el precio normal
                precio = articulo.producto.precio
                cantidad = articulo.cantidad
                subtotal += precio * cantidad

        # El total es igual al subtotal en este caso (sin descuentos aplicados)
        total = subtotal

        # Serializar el carrito y los elementos del carrito
        carrito_serializado = CarritoSerializer(cart)
        cartitem_serializado = ItemCarritoSerializer(cartitems, many=True)

        # Formatear subtotal y total
        subtotalFormato = "{:,.0f}".format(subtotal).replace(",", ".")
        totalFormato = "{:,.0f}".format(total).replace(",", ".")

        # Retornar los datos en formato JSON
        return Response({
            "carrito": carrito_serializado.data,
            "articulo_carrito": cartitem_serializado.data,
            "subtotal": subtotalFormato,
            "total": totalFormato,
            "contador": len(cartitems),  # Contar los elementos del carrito
        }, status=status.HTTP_200_OK)

    except Exception as e:
        # Manejar errores y retornar una respuesta de error
        return Response({"error": "Ha ocurrido un error al procesar la solicitud"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addAPI(request):
    data = request.data
    producto_id = data.get("id")

    # Verificar si el producto existe
    producto = get_object_or_404(Producto, id=producto_id)

    # Obtener el carrito del usuario autenticado o crear uno nuevo para el usuario anónimo
    if request.user.is_authenticated:
        cart, created = Carrito.objects.get_or_create(usuario=request.user, completed=False)
    else:
        session_id = request.session.get("nonuser")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["nonuser"] = session_id
        cart, created = Carrito.objects.get_or_create(session_id=session_id, completed=False)

    # Verificar si el item ya está en el carrito y actualizar su cantidad, o crear uno nuevo
    try:
        item = ItemCarrito.objects.get(carrito=cart, producto=producto)
        if item.cantidad < producto.stock:
            item.cantidad += 1
            item.save()
        else:
            return Response({"message": "La cantidad solicitada excede el stock disponible"}, status=status.HTTP_400_BAD_REQUEST)
    except ItemCarrito.DoesNotExist:
        if producto.stock > 0:
            # item = ItemCarrito.objects.create(carrito=cart, producto=producto, cantidad=1)
            item = ItemCarrito.objects.create(carrito=cart, producto=producto)
        else:
            return Response({"message": "El producto está agotado"}, status=status.HTTP_400_BAD_REQUEST)

    # Serializar la respuesta
    carrito_serializer = CarritoSerializer(cart)
    item_carrito_serializer = ItemCarritoSerializer(item)

    # Devolver la respuesta con los datos serializados
    return Response({
        "carrito": carrito_serializer.data,
        "item_carrito": item_carrito_serializer.data,
    }, status=status.HTTP_200_OK)
    # return Response({item_carrito_serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def updateAPI(request):
    try:
        data = request.data
        producto_id = data.get("id")
        cantidad_str = data.get("cantidad")

        producto = Producto.objects.get(id=producto_id)

        # Verificar si la cantidad es un entero válido y si es menor que cero
        try:
            nueva_cantidad = int(cantidad_str)
            if nueva_cantidad < 0:
                return Response({"error": "No se permite valores negativos en la cantidad"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "La cantidad debe ser un número entero válido"}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si la cantidad solicitada excede el stock disponible
        if producto.stock < nueva_cantidad:
            return Response({"error": "La cantidad solicitada excede el stock disponible"}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener o crear el carrito
        if request.user.is_authenticated:
            cart, created = Carrito.objects.get_or_create(usuario=request.user, completed=False)
        else:
            try:
                cart = Carrito.objects.get(session_id=request.session["nonuser"], completed=False)
            except Carrito.DoesNotExist:
                request.session["nonuser"] = str(uuid.uuid4())
                cart = Carrito.objects.create(session_id=request.session["nonuser"], completed=False)

        # Actualizar la cantidad del producto en el carrito
        try:
            cartitem = ItemCarrito.objects.get(carrito=cart, producto=producto)
            if nueva_cantidad == 0:
                cartitem.delete()
            else:
                cartitem.cantidad = nueva_cantidad
                cartitem.save()
        except ItemCarrito.DoesNotExist:
            if nueva_cantidad != 0:
                ItemCarrito.objects.create(carrito=cart, producto=producto, cantidad=nueva_cantidad)

        return Response({"message": "Se actualizó la cantidad del producto"})

    except Producto.DoesNotExist:
        return Response({"error": "Producto no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def eliminarAPI(request):
    # Se obtiene el ID del producto del cuerpo de la solicitud JSON
    data = request.data
    producto_id = data.get("id")

    # Se verifica si se proporcionó el ID del producto
    if not producto_id:
        return Response({"error": "ID del producto no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Se busca el producto por su ID en la base de datos
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        # Si el producto no existe, se devuelve un error
        return Response({"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    # Se verifica si el usuario está autenticado
    if request.user.is_authenticated:
        # Si está autenticado, se obtiene el carrito asociado al usuario
        cart, _ = Carrito.objects.get_or_create(usuario=request.user, completed=False)
    else:
        # Si no está autenticado, se obtiene el carrito asociado a la sesión del usuario anónimo
        cart_id = request.session.get("nonuser")
        if not cart_id:
            return Response({"error": "El carrito no existe"}, status=status.HTTP_404_NOT_FOUND)
        cart, _ = Carrito.objects.get_or_create(session_id=cart_id, completed=False)
    try:
        # Se busca el elemento del carrito asociado al carrito y al producto
        cartitem = ItemCarrito.objects.get(carrito=cart, producto=producto)
        cartitem.delete()
        # Se devuelve una respuesta indicando la eliminación exitosa
        return Response({"message": "Producto eliminado del carrito"}, status=status.HTTP_200_OK)        
    except ItemCarrito.DoesNotExist:
        # Si el elemento del carrito no existe, se devuelve una respuesta indicando que no se encontró el producto
        return Response({"message": "Producto no encontrado en el carrito"}, status=status.HTTP_404_NOT_FOUND)
from django.http import JsonResponse
from .models import Carrito, ItemCarrito
from tienda.models import Producto
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

import pdb
    # pdb.set_trace() 

def mostrar_carrito(request):
    cartitems = []
    descuento = 0
    subtotal = 0
    cantidad = 0
    contador = 0
    total = 0
    cart = None

    if request.user.is_authenticated:
        cart, created = Carrito.objects.get_or_create(usuario=request.user, completed=False)
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
         
        # cartitems almacena todo los productos del carrito  
        cartitems = cart.cartitems.all()
        # Utilizamos este metodo count() para contar cuantos objetos ahi en el carrito
        contador = cartitems.count()

    subtotalFormato  = "{:,.0f}".format(subtotal).replace(',', '.')
    totalFormato = "{:,.0f}".format(total).replace(',', '.')
    return dict(articulo_carrito=cartitems, subtotal=subtotalFormato, total=totalFormato, contador=contador)

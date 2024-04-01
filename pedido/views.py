from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PedidoForm, PagoForm
from .models import Pedido, Pago, DetallePedido, Departamento, Municipio, Ventas
from tienda.models import Producto
from carrito.models import Carrito, ItemCarrito
from django.contrib import messages
from django.utils import timezone

# Nos permiten ejecutar el pago si es valido
from django.db.models.signals import post_save
from django.dispatch import receiver

# Correo electronico
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from cuenta.models import Cuenta

# API
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import PedidoSerializer

import logging

logger = logging.getLogger(__name__)

import datetime

from django.db import transaction

import pdb


@login_required(login_url="inicio_sesion")
def realizar_pedido(request):
    total=0    

    # Listar los departamentos
    queryset = Departamento.objects.all().order_by("nombre")

    cart = Carrito.objects.get(usuario=request.user, completed=False)
    item = ItemCarrito.objects.filter(carrito=cart)
    
    if item.count() <= 0:
        return redirect("tienda")

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


    if request.method == "POST":
        formulario = PedidoForm(request.POST)
        if formulario.is_valid():
            data = Pedido()
            data.usuario = request.user    
            data.nombre = formulario.cleaned_data["nombre"]
            data.apellido = formulario.cleaned_data["apellido"]
            data.telefono = formulario.cleaned_data["telefono"]
            data.correo_electronico = formulario.cleaned_data["correo_electronico"]
            data.direccion = formulario.cleaned_data["direccion"]
            data.direccion_local = formulario.cleaned_data["direccion_local"]
            data.codigo_postal = formulario.cleaned_data["codigo_postal"]
            data.total_pedido = total
            # Se guarda para obtener el id, y ser utilizado en el numero del pedido
            data.save()

            cod_departamento = request.POST.get("selectDepartamento")
            departamento = Departamento.objects.get(codigo=cod_departamento)
            data.departamento = departamento.nombre

            cod_municipio = request.POST.get("selectMunicipio")
            municipio = Municipio.objects.filter(
                codigo=cod_municipio, codigo_departamento=cod_departamento
            ).first()
            data.municipio = municipio.nombre

            # Numero del pedido: fecha del año, mes, y dia
            year = int(datetime.date.today().strftime("%Y"))
            months = int(datetime.date.today().strftime("%m"))
            day = int(datetime.date.today().strftime("%d"))

            dt = datetime.date(year, months, day)
            fecha_actual = dt.strftime("%Y%m%d")
            # 2024 02 06 1.. ingremento por el id de cada pedido
            num_pedido = fecha_actual + str(data.id)
            data.numero_pedido = num_pedido
            data.save()

            # Redirigir a la página de pago con el ID del pedido
            return redirect("pago", id_pedido=data.pk)
    else:
        formulario = PedidoForm()
    return render(
        request,
        "client/pedido/realizar_pedido.html",
        {"form": formulario, "departamneto": queryset},
    )


def regiones(request):
    codigo_departamento = request.GET.get("codigo_departamento")
    municipios = Municipio.objects.filter(codigo_departamento=codigo_departamento)
    lista = list(municipios.values("codigo", "nombre"))
    return JsonResponse({"municipios": lista})


@login_required(login_url="inicio_sesion")
def pago(request, id_pedido):
    pedido = get_object_or_404(Pedido, pk=id_pedido)
    if request.method == "POST":
        formulario = PagoForm(request.POST, request.FILES)
        if formulario.is_valid():
            data = Pago()
            data.metodo_pago = formulario.cleaned_data["metodo_pago"]
            data.comprobante = formulario.cleaned_data["comprobante"]
            data.usuario = request.user
            data.cantidad_pagada = pedido.total_pedido
            data.save()

            pedido.pago = data
            pedido.save()

            messages.success(
                request, "Pago exitoso, Se verificara si el comprobante es valido"
            )
            return redirect("index")
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        formulario = PagoForm()
    return render(
        request, "client/pedido/pago.html", {"pedido": pedido, "form": formulario}
    )


@receiver(post_save, sender=Pago)
def email_info_pedido(sender, instance, **kwargs):
    usuario = instance.usuario     
    # __usuario: Acceso a un campo relacionado entre modelos
    # _usuario: Acceso directo a un campo del modelo actual
    cart = Carrito.objects.get(usuario=usuario, completed=False)    
    cartItem = ItemCarrito.objects.filter(carrito=cart)    
    pedido = Pedido.objects.filter(usuario=usuario)
    pago = Pago.objects.filter(usuario=usuario).first()    
    venta = Ventas()        
    
    # Es necesario iterar en for, para que se envie el correo al usuario acctual
    for ped in pedido:
        ped.ordenado = True
        ped.save() 

    if instance.estado_pago == "Aprobado" and instance.estado_envio == "Enviado":
        if cartItem and pedido and pago:        

            for item in cartItem:                                    
                venta.pedido = ped
                venta.pago = pago
                venta.usuario_id = usuario.id
                venta.producto_id = item.producto_id
                venta.cantidad = item.cantidad
                venta.precio = item.producto.precio
                venta.total = ped.total_pedido                
                venta.save()
    
                # STOCK
                prod = Producto.objects.get(pk=item.producto_id)
                prod.stock -= item.cantidad
                prod.save()
    
                # Elimina los producto del carrito
                item.delete()    
    
        mail_subject = "¡Su pedido ha sido aprobado!"
        mensaje = render_to_string(
            "client/pedido/email_pago.html",
            {"venta": venta},
        )
        to_email = ped.correo_electronico
        send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
        send_email.attach_alternative(mensaje, "text/html")
        send_email.send()            
    else:
        mail_subject = "¡El pedido ha sido cancelado!"
        mensaje = render_to_string(
            "client/pedido/email_pago_cancelado.html",
            {"venta": venta},
        )

        to_email = ped.correo_electronico
        send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
        send_email.attach_alternative(mensaje, "text/html")
        send_email.send()

        logger.info("Correo electrónico de cancelación enviado correctamente.")


# def actualizar_stock(usuario):
#     cartItem = ItemCarrito.objects.filter(carrito__usuario=usuario).first()
#     pedido = Pedido.objects.filter(usuario=usuario).first()
#     pago = Pago.objects.filter(usuario=usuario).first()
#     if cartItem and pedido and pago:
#         pedido.ordenado = True
#         pedido.save()

#         venta = Ventas()
#         venta.pedido = pedido
#         venta.pago = pago
#         venta.usuario_id = usuario.id
#         venta.producto_id = cartItem.producto_id
#         venta.cantidad = cartItem.cantidad
#         venta.precio = cartItem.producto.precio
#         venta.fecha = timezone.now()
#         venta.save()

#         prod = Producto.objects.get(pk=cartItem.producto_id)
#         prod.stock -= cartItem.cantidad
#         prod.save()

#         # Elimina los producto del carrito
#         cartItem.delete()


def historial_compra(request):
    querset = Ventas.objects.filter(usuario=request.user)
    return render(request, "client/pedido/historial_compra.html", {"ventas":querset})


# ? API


@api_view(["GET", "POST"])
def orderAPIView(request):
    if request.method == "POST":
        serializer = PedidoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PedidoForm, PagoForm
from .models import Pedido, Pago, Ventas, DetallePedido, Departamento, Municipio
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

import datetime

from django.db import transaction

import pdb


@login_required(login_url="inicio_sesion")
def realizar_pedido(request, total=0):
    usuario_actual = request.user
    print("usuario pedido", usuario_actual)

    # Listar los departamentos
    queryset = Departamento.objects.all().order_by("nombre")

    if request.method == "POST":
        formulario = PedidoForm(request.POST)
        if formulario.is_valid():
            data = Pedido()
            data.usuario = usuario_actual
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

    pedido = Pedido.objects.filter(usuario=usuario)
    for datos in pedido:
        datos.ordenado = True
        datos.save()

    if instance.estado_pago == "Aprobado" and instance.estado_envio == "Enviado":

        mail_subject = "¡Su pedido ha sido aprobado!"
        mensaje = render_to_string(
            "client/pedido/email_pago.html",
            {"pedido": datos},
        )

        to_email = datos.correo_electronico
        send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
        send_email.attach_alternative(mensaje, "text/html")
        send_email.send()

        # Pago correcto, se actualiza el stock
        actualizar_stock(instance)
    else:
        mail_subject = "¡El pedido ha sido cancelado!"
        mensaje = render_to_string(
            "client/pedido/email_pago_cancelado.html",
            {"pedido": datos},
        )

        to_email = datos.correo_electronico
        send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
        send_email.attach_alternative(mensaje, "text/html")
        send_email.send()


def actualizar_stock(request):
    cartItem = ItemCarrito.objects.filter(carrito__usuario=request.user)
    pedido = Pedido.objects.filter(usuario=request.user)
    pago = Pago.objects.filter(usuario=request.user)
    for item in cartItem:
        venta = Ventas.objects.create(
            cartItem=item,
            pedido=pedido,
            pago=pago,
            usuario=request.user,
            fecha=timezone.now(),
        )
        venta.save()
        prod = Producto.objects.get(pk=item.producto_id)
        prod.stock -= item.cantidad
        prod.save()
        # Elimina los producto del carrito
        item.delete()



def historial_compra(request):
    return render(request, "client/pedido/historial_compra.html")

# ? API


@api_view(["GET", "POST"])
def orderAPIView(request):
    if request.method == "POST":
        serializer = PedidoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

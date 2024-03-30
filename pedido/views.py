from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PedidoForm, PagoForm
from .models import Pedido, Pago, Ventas, DetallePedido, Departamento, Municipio
from tienda.models import Producto
from carrito.models import Carrito
from django.contrib import messages

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
    departamneto = Departamento.objects.all()

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
            data.departamento = formulario.cleaned_data["departamento"]
            data.ciudad = formulario.cleaned_data["ciudad"]
            data.codigo_postal = formulario.cleaned_data["codigo_postal"]
            data.total_pedido = total
            data.save()  # Guarda el pedido, para hacer uso del ID en el numero de pedido

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

            # Crear los detalles de pedido para cada producto en el carrito
            # for item in items:
            #     producto = item["producto"]
            #     cantidad = item["cantidad"]
            #     subtotal = item["subtotal"]

            #     # totalFormato = "{:,.0f}".format(totalFormato).replace(",", ".")
            #     # subTotalFormato = "{:,.0f}".format(subtotal).replace(",", ".")

            #     DetallePedido.objects.create(
            #         pedido=data,
            #         producto=producto,
            #         cantidad=cantidad,
            #         ordenado=False,
            #         subtotal=subtotal,
            #         total=totalFormato,
        #     )
    else:
        formulario = PedidoForm()
    return render(
        request,
        "client/pedido/realizar_pedido.html",
        {"form": formulario, "departamneto": departamneto},
    )


def regiones(request):
    codigo_departamento = request.GET.get("codigo_departamento")
    municipios = Municipio.objects.filter(codigo_departamento=codigo_departamento)
    lista = list(municipios.values("codigo", "nombre"))
    return JsonResponse({"municipios": lista})


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
    if instance.estado_pago == "Aprobado" and instance.estado_envio == "Enviado":
        usuario = instance.usuario

        pedido = Pedido.objects.filter(usuario=usuario)
        for datos in pedido:
            datos.ordenado = True
            datos.save()

        mail_subject = "¡Su pedido ha sido aprobado!"
        mensaje = render_to_string(
            "client/pedido/email_pago.html",
            {"pedido": datos},
        )

        to_email = datos.correo_electronico
        send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
        send_email.attach_alternative(mensaje, "text/html")
        send_email.send()

        actualizar_stock(instance)
        # pdb.set_trace()


def actualizar_stock(request):
    pass
    # cart.limpiar_carrito()

    # detalle_pedido = DetallePedido.objects.filter(pedido__usuario=usuario)
    # for detalle in detalle_pedido:
    #     if detalle.pedido.ordenado:
    #         producto = detalle.producto
    #         cantidad = detalle.cantidad
    #         print("producto stock", producto)
    #         print("cantidad stock", cantidad)
    #         producto.stock -= cantidad
    #         producto.save()
    # producto.delete()
    # pdb.set_trace()


# ? API


@api_view(["GET", "POST"])
def orderAPIView(request):
    if request.method == "POST":
        serializer = PedidoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

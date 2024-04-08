from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido, Pago, Departamento, Municipio, Ventas
from django.contrib.auth.decorators import login_required
from .forms import PedidoForm, PagoForm, PagosForms
from carrito.models import Carrito, ItemCarrito
from django.http import JsonResponse
from config.decorators import protect_route
from django.contrib import messages
from tienda.models import Producto
# Nos permiten ejecutar el pago si es valido
from django.db.models.signals import post_save
from django.dispatch import receiver
# Correo electronico
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from cuenta.models import Cuenta
# API
from .serializers import PedidoSerializer, DepartamentoSerializer, MunicipioSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.db.models.functions import TruncDate,TruncDay, TruncWeek, TruncMonth, TruncYear
from datetime import timedelta, timezone
from django.db.models import Sum
import datetime

import pdb


@login_required(login_url="inicio_sesion")
def realizar_pedido(request):
    total = 0
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

            mail_subject = "¡Su pedido está en verificación!"
            mensaje = render_to_string(
                "client/pedido/email_pedido.html",
                {"pedido": data},
            )
        
            to_email = data.correo_electronico
            send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
            send_email.attach_alternative(mensaje, "text/html")
            send_email.send()

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



@api_view(['POST'])
def pedidoAPI(request):
    total = 0

    # Obtener los datos del pedido del cuerpo de la solicitud
    data = request.data

    # Calcular el total del pedido
    # (Nota: Este cálculo puede necesitar ajustes dependiendo de cómo esté estructurado tu modelo)
    for articulo in data['items']:
        if articulo['producto']['aplicar_descuento']:
            descuento = articulo['producto']['aplicar_descuento']
            cantidad = articulo['cantidad']
            subtotal = descuento * cantidad
            total += subtotal
        else:
            precio = articulo['producto']['precio']
            cantidad = articulo['cantidad']
            subtotal = precio * cantidad
            total += subtotal

    # Validar y guardar el pedido
    serializer = PedidoSerializer(data=data)
    if serializer.is_valid():
        pedido = serializer.save(total_pedido=total)
        return Response({'id_pedido': pedido.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def departamentos_api(request):
    if request.method == 'GET':
        departamentos = Departamento.objects.all()
        serializer = DepartamentoSerializer(departamentos, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def municipios_por_departamento_api(request):
    codigo_departamento = request.GET.get('codigo_departamento')
    municipios = Municipio.objects.filter(codigo_departamento=codigo_departamento)
    serializer = MunicipioSerializer(municipios, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def realizar_pedido_api(request):
    if request.method == 'POST':
        # Recuperar el carrito del usuario
        cart = Carrito.objects.get(usuario=request.user, completed=False)
        items_carrito = ItemCarrito.objects.filter(carrito=cart)

        # Calcular el total del pedido
        total = 0
        for item in items_carrito:
            if item.producto.aplicar_descuento:
                descuento = item.producto.aplicar_descuento()
                subtotal = descuento * item.cantidad
                total += subtotal
            else:
                precio = item.producto.precio
                subtotal = precio * item.cantidad
                total += subtotal

        # Validar el formulario de pedido
        pedido_serializer = PedidoSerializer(data=request.data)
        if pedido_serializer.is_valid():
            # Guardar el pedido con el total calculado
            pedido = pedido_serializer.save(total_pedido=total, usuario=request.user)

            # Generar el número de pedido
            year = int(datetime.date.today().strftime("%Y"))
            months = int(datetime.date.today().strftime("%m"))
            day = int(datetime.date.today().strftime("%d"))
            dt = datetime.date(year, months, day)
            fecha_actual = dt.strftime("%Y%m%d")
            num_pedido = fecha_actual + str(pedido.id)
            pedido.numero_pedido = num_pedido
            pedido.save()

            # Enviar correo electrónico de notificación al usuario
            mail_subject = "¡Su pedido está en verificación!"
            mensaje = render_to_string(
                "client/pedido/email_pedido.html",
                {"pedido": pedido},
            )
            to_email = pedido.correo_electronico
            send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
            send_email.attach_alternative(mensaje, "text/html")
            send_email.send()

            return Response({"pedido_id": pedido.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(pedido_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                request, "Pago exitoso. Se verificará si el comprobante es válido"
            )
            return redirect("index")
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
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

    # Es necesario iterar en for, para que se envie el correo al usuario acctual
    for ped in pedido:
        ped.ordenado = True
        ped.save()

    if instance.estado_pago == "Aprobado" and instance.estado_envio == "Enviado":
        if cartItem and pedido and pago:
            # Lista para almacenar todas las ventas realizadas
            list_prod_venta = []
            for item in cartItem:
                venta = Ventas()
                venta.pedido = ped
                venta.pago = pago
                venta.usuario_id = usuario.id
                venta.producto_id = item.producto_id
                venta.cantidad = item.cantidad
                venta.precio = item.producto.precio
                venta.total = ped.total_pedido
                venta.save()

                list_prod_venta.append(venta)

                # Stock
                prod = Producto.objects.get(pk=item.producto_id)
                prod.stock -= item.cantidad
                prod.save()

                # Elimina los producto del carrito
                item.delete()

        mail_subject = "¡Su pedido ha sido aprobado!"
        mensaje = render_to_string(
            "client/pedido/email_pago.html",
            {"producto": list_prod_venta, "venta": venta},
        )
        # to_email = ped.correo_electronico
        to_email = ped.correo_electronico
        send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
        send_email.attach_alternative(mensaje, "text/html")
        send_email.send()
    elif instance.estado_pago == "Rechazado" and instance.estado_envio == "Rechazado":
        mail_subject = "¡El pedido ha sido cancelado!"
        mensaje = render_to_string(
            "client/pedido/email_pago_cancelado.html",
            {"venta": ped},
        )

        to_email = ped.correo_electronico
        send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
        send_email.attach_alternative(mensaje, "text/html")
        send_email.send()


def historial_compra(request):
    querset = Ventas.objects.filter(usuario=request.user).order_by("-fecha")
    return render(request, "client/pedido/historial_compra.html", {"ventas": querset})


# ? ADMIN
@login_required(login_url="inicio_sesion")
@protect_route
def lista_pedido(request):
    queryset = Pedido.objects.all()
    return render(
        request,
        "admin/pedido/lista_pedido.html",
        {"pedido": queryset},
    )


@login_required(login_url="inicio_sesion")
@protect_route
def lista_venta(request):
    # fecha_hoy = datetime.now()
    queryset = Ventas.objects.all()
    return render(
        request,
        "admin/venta/lista_venta.html",
        {"ventas": queryset},
    )


@login_required(login_url="inicio_sesion")
@protect_route
def lista_pagos(request):
    queryset = Pago.objects.all()
    return render(
        request,
        "admin/pagos/lista_pagos.html",
        {"pagos": queryset},
    )


@login_required(login_url="inicio_sesion")
@protect_route
def detalle_pagos_admin(request, id_pagos):    
    detalle_pagos = get_object_or_404(Pago, pk=id_pagos)           
    form = PagosForms(request.POST, instance=detalle_pagos)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "La verificación del pago fue actualizada")
            return redirect("lista_pagos")
        else:
            messages.error(request, "Ha ocurrido un error en el formulario")
    return render(
        request,
        "admin/pagos/detalle_pagos.html",
        {"detalle": detalle_pagos, "form": form})
    

# @login_required(login_url="inicio_sesion")
# @protect_route
# def eliminar_pagos(request, id_pagos):
#     pagos = get_object_or_404(Pago, id=id_pagos)
#     if request.method == "POST":
#         pagos.delete()
#         messages.success(request, "Pago eliminada")
#         return redirect("lista_pagos")
#     else:
#         messages.error(request, "Ha ocurrido un error al eliminar un pago")

# ? API
@api_view(["GET"])
def regionesAPI(request):
    codigo_departamento = request.GET.get("codigo_departamento")
    municipios = Municipio.objects.filter(codigo_departamento=codigo_departamento)
    lista = list(municipios.values("codigo", "nombre"))
    return Response({"municipios": lista})



@api_view(["GET", "POST"])
def orderAPIView(request):
    if request.method == "POST":
        serializer = PedidoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

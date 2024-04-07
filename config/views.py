from django.contrib.auth.decorators import login_required
from .decorators import protect_route
from django.shortcuts import render
from tienda.models import Producto
from pedido.models import Ventas

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from tienda.serializers import ProductoSerializer

from django.db.models.functions import TruncDate, TruncDay, TruncWeek, TruncMonth, TruncYear
from datetime import timedelta, timezone
from django.db.models import Sum
import datetime


# Client
def index(request):
    productos = Producto.objects.all().filter(disponible=True)
    return render(request, "index.html", {"producto": productos})


@api_view(["GET"])
def listProductAPIView(request):
    queryset = Producto.objects.all().filter(disponible=True)
    serializer = ProductoSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Admin
@login_required(login_url="inicio_sesion")
@protect_route
def dashboard(request):
    # annotate(): calcula(suma,promedio,max,min) y agregra nuevas columnas a la consulta
    ventas_dia = Ventas.objects.annotate(dia=TruncDate('fecha')).values('dia').annotate(total_ventas=Sum('total'))[:5]
    ventas_week = Ventas.objects.annotate(mes=TruncWeek('fecha')).values('mes').annotate(total_ventas=Sum('total'))[:5]
    ventas_month = Ventas.objects.annotate(anio=TruncMonth('fecha')).values('anio').annotate(total_ventas=Sum('total'))[:5]   
    
    prod_mas_vendido = Ventas.objects.values('producto__nombre','producto__precio').annotate(total_ventas=Sum('total'))[:5]
    
    # aggregate(): modifica valores
    ingresos_totales = Ventas.objects.aggregate(ingresos=Sum('total'))
    
    venta_usuario = Ventas.objects.values('usuario__correo_electronico').annotate(total_ventas=Sum('total')).order_by('-total')[:5]
    
    precio_mayor = Producto.objects.order_by('-precio')[:5]
    stock_mayor = Producto.objects.order_by('-stock')[:5]
    stock_menor = Producto.objects.order_by('stock')[:5]
                    
    return render(
        request,
        "dashboard.html",
        {"ventas_dia": ventas_dia,
         "ventas_week": ventas_week,
         "ventas_month":ventas_month,
         "prod_mas_vendido":prod_mas_vendido,
         "ingresos_totales":ingresos_totales,
         "venta_usuario":venta_usuario,
         "precio_mayor":precio_mayor,
         "stock_mayor":stock_mayor,
         "stock_menor":stock_menor}
    )





# Footer
def sobre_nosotros(request):
    return render(request, "client/footer/sobre_nosotros.html")

def politicas_privacidad(request):
    return render(request, "client/footer/politicas_de_privacidad.html")

def metodo_pago(request):
    return render(request, "client/footer/metodo_pago.html")

def terminos_condiciones(request):
    return render(request, "client/footer/terminos_y_condiciones.html")

def manuales(request):
    return render(request, "client/footer/manuales.html")
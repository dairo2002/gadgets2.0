from django.contrib.auth.decorators import login_required
from .decorators import protect_route
from django.shortcuts import render
from tienda.models import Producto, Categoria
from pedido.models import Pago, Pedido, Ventas
from cuenta.models import Cuenta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from tienda.serializers import ProductoSerializer

from django.db.models.functions import TruncDate, TruncDay, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta
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
    cuenta = Cuenta.objects.filter(is_active=True).count()
    venta = Ventas.objects.all().count()
    pedido = Pedido.objects.filter(ordenado=True).count()
    pago = Pago.objects.all().count()
    
    fecha_actual = timezone.now()

    ventas_dia = Ventas.objects.filter(fecha__date=fecha_actual.date())
    
    inicio_semana = fecha_actual - timedelta(days=fecha_actual.weekday())
    fin_semana = inicio_semana + timedelta(days=7)
    ventas_semana = Ventas.objects.filter(fecha__date__range=[inicio_semana, fin_semana])
        
    prod_mas_vendido = Ventas.objects.values('producto__nombre','producto__precio','cantidad',).annotate(total_ventas=Sum('total'))[:5]
    
    precio_mayor = Producto.objects.order_by('-precio')[:5]
    stock_mayor = Producto.objects.order_by('-stock')[:5]
    stock_menor = Producto.objects.order_by('stock')[:5]
                    
    return render(
        request,
        "dashboard.html",
        {"ventas_dia": ventas_dia,
         "ventas_week": ventas_semana,     
         "prod_mas_vendido":prod_mas_vendido,  
         "precio_mayor":precio_mayor,
         "stock_mayor":stock_mayor,
         "stock_menor":stock_menor,
         "cuenta":cuenta,
         'ventas':venta,
         "pedidos":pedido,
         "pagos":pago
         }
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
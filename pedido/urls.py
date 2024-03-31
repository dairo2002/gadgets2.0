from django.urls import path
from . import views

urlpatterns = [                        
    path("realizar_pedido/", views.realizar_pedido, name='realizar_pedido' ), 
    path("regiones/", views.regiones, name='regiones' ),            
    path("pago/<int:id_pedido>/", views.pago, name='pago' ),
    path("mis_compras/", views.historial_compra, name='historial_compras' ),
]
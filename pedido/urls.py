from django.urls import path
from . import views

urlpatterns = [                        
    path("realizar_pedido/", views.realizar_pedido, name='realizar_pedido' ),
    # path("pago/", views.pago, name='pago' ),
    path("pago/<int:id_pedido>/", views.pago, name='pago' ),
]
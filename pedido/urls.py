from django.urls import path
from . import views

urlpatterns = [                        
    path("regiones/", views.regiones, name='regiones' ),            
    path("realizar_pedido/", views.realizar_pedido, name='realizar_pedido'), 
    path("pago/<int:id_pedido>/", views.pago, name='pago' ),
    path("mis_compras/", views.historial_compra, name='historial_compras' ),

        # ADMIN
    path("admin/pedido/", views.lista_pedido, name="lista_pedido"),
    path("admin/pedido/<int:id_pedido>/", views.detalle_pedido_admin, name="detalle_pedido_admin"),
    path("admin/pedido/<int:id_pedido>/eliminar", views.eliminar_pedido, name="eliminar_pedido"),
    
    path("admin/venta/", views.lista_venta, name="lista_venta"),
    path("admin/venta/<int:id_venta>/", views.detalle_venta_admin, name="detalle_venta_admin"),
    path("admin/venta/<int:id_venta>/eliminar", views.eliminar_venta, name="eliminar_venta"),

    path("admin/pagos/", views.lista_pagos, name="lista_pagos"),
    path("admin/pagos/<int:id_pagos>/", views.detalle_pagos_admin, name="detalle_pagos_admin"),
    path("admin/pagos/<int:id_pagos>/eliminar", views.eliminar_pagos, name="eliminar_pagos"),
]
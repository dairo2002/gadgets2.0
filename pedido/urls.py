from django.urls import path
from . import views

urlpatterns = [                        
    path("regiones/", views.regiones, name='regiones' ),            
    path("realizar_pedido/", views.realizar_pedido, name='realizar_pedido'), 
    path("pago/<int:id_pedido>/", views.pago, name='pago' ),    
    # path("mis_compras/", views.historial_compra, name='historial_compras' ),
    path("mis_pedidos/", views.historial_pedidos, name='historial_pedidos' ),

    # ADMIN
    path("admin/pedido/", views.lista_pedido, name="lista_pedido"),
    path("admin/venta/", views.lista_venta, name="lista_venta"),
    path("admin/pagos/", views.lista_pagos, name="lista_pagos"),
    path("admin/pagos/<int:id_pagos>/", views.detalle_pagos_admin, name="detalle_pagos_admin"),
    # path("admin/pagos/<int:id_pagos>/eliminar", views.eliminar_pagos, name="eliminar_pagos"),
    # APIS  
    
    # path("api/v1/regiones/", views.regionesAPI),
    path("api/v1/realizar_pedidos/", views.pedidoAPI),
    path("api/v1/historial_pedidos/", views.historial_pedidosAPI),
    path("api/v1/departamento/", views.departamentos_api),
    path("api/v1/municipio/", views.municipios_por_departamento_api),
    path("api/v1/realizar_pedido/", views.realizar_pedido_api),    
     
    
]
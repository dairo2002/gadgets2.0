from django.urls import path
from . import views

urlpatterns = [        
    path("", views.mostrar_carrito, name="mostrar_carrito"),
    path("agregar_carrito/", views.add, name="add_carrito"),
    # path("actualizar_carrito/<int:producto_id>/", views.update, name="update_carrito"), 
    path("actualizar_carrito/", views.update, name="update_carrito"), 
    path("eliminar_carrito/", views.delete, name="delete_carrito"), 

    
    path("eliminar_cantidad/<int:producto_id>/<int:carrito_id>/", views.delete_cantidad_carrito, name="eliminar_cantidad"),
    path("eliminar_producto_carrito/<int:producto_id>/<int:carrito_id>/", views.delete_producto_carrito, name="eliminar_producto_carrito"),

    # ? API
    path("api/v1/agregar_carrito/", views.addAPI),
]

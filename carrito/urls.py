from django.urls import path
from . import views

urlpatterns = [        
    path("", views.mostrar_carrito, name="mostrar_carrito"),
    path("agregar_carrito/", views.add, name="add_carrito"),
    path("actualizar_carrito/", views.updates, name="updates"),
    path("eliminar_carrito/", views.delete, name="delete_carrito"), 

    # ? API
    path("api/v1/mostrar_carrito/", views.mostrar_carritoAPI),
    path("api/v2/mostrar_carrito/", views.mostrar_carrito_api),
    path("api/v1/agregar_carrito/", views.addAPI),
    path("api/v1/actualizar_carrito/", views.updateAPI),
    path("api/v1/eliminar_carrito/", views.eliminarAPI),


]

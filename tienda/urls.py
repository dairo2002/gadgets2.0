from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.tienda, name="tienda"),
    # Esta ruta muestra los productos que pertenecen a una categoria
    # name="categoria_a_producto" viene del modelo
    path("categoria/<slug:categoria_slug>/", views.tienda, name="categoria_a_producto"),
    # Ruta de una categoria de un producto, que va hacia el detelle del producto
    path(
        "categoria/<slug:categoria_slug>/<slug:producto_slug>/",
        views.detalle_producto,
        name="detalle_producto",
    ),
    # Ruta busqueda de un producto
    path("buscar/", views.filtro_buscar_producto, name="buscar_producto"),
    path("filtro_precio/", views.filtro_rango_precios, name="filtro_precios"),
    # ? APIS
    # Lista de categorías
    path("api/v1/lista_categorias/", views.listCategory),
    # Productos de una categoria
    path("api/v1/store/<int:category_id>/", views.store_categ_prod),
    # Versiones detalle de un producto
    path("api/v1/detail_product/<int:product_id>/", views.detail_products),
  
    # Filtros
    path("api/v1/search_product/", views.searchProductAPIView),
    path("api/v2/search_product/", views.searchProductAPI),
    path("api/v1/range_price/", views.range_priceAPIView),
    # ? ADMIN
    path("admin/productos/", views.listar_productos, name="lista_productos"),
    path("admin/productos/<int:id_producto>/",views.detalle_producto_admin,name="detalle_producto_admin"),
    path("admin/productos/<int:id_producto>/eliminar",views.eliminar_producto,name="eliminar_producto"),

    path("admin/categorias/", views.lista_categorias, name="lista_categorias"),
    path("admin/categorias/<int:id_categoria>/", views.detalle_categoria_admin, name="detalle_categoria_admin"),
    path("admin/categorias/<int:id_categoria>/eliminar", views.eliminar_categoria, name="eliminar_categoria"),
]

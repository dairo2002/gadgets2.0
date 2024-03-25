from .models import Categoria, Producto


def enlaces_categorias(request):
    enlace = Categoria.objects.all()
    # dict=diccionario
    return dict(enlace_categoria=enlace)



# def rango_precios(request):
#     rango_precio = [
#         [0, 10000],
#         [20000, 30000],
#         [40000, 50000],
#     ]

#     productos = Producto.objects.all().order_by("precio")
#     producto_por_rango = {}
#     for rango in rango_precio:
#         producto_por_rango[rango] = list(
#             producto for producto in productos if rango[0] <= producto.precio < rango[1]
#         )

#     return dict(rango_precio=producto_por_rango)

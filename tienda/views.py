from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Producto, Categoria, Valoraciones
from pedido.models import Pedido
from carrito.models import Carrito
from django.contrib import messages
from .forms import ValoracionesForm, ProductoForm

# Q es utilizado para consultas complejas
from django.db.models import Q

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# API
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import ProductoSerializer, CategoriaSerializer


# Tienda de productos que pertenecen a una categoria
def tienda(request, categoria_slug=None):
    if categoria_slug is not None:
        categorias = get_object_or_404(Categoria, slug=categoria_slug)
        productos = (
            Producto.objects.all()
            .filter(categoria=categorias, disponible=True)
            .order_by("nombre")
        )
        contar_productos = productos.count()

        # ? Paginacion

        paginacion = Paginator(productos, 6)
        pagina_numero = request.GET.get("pagina")
        pagina_producto = paginacion.get_page(pagina_numero)

    else:
        # Si no se proporciona un slug de categoría, mostramos todos los productos disponibles ordenados por ID
        productos = Producto.objects.all().filter(disponible=True).order_by("nombre")
        contar_productos = productos.count()
        paginacion = Paginator(productos, 9)
        pagina_numero = request.GET.get("pagina")
        pagina_producto = paginacion.get_page(pagina_numero)
    return render(
        request,
        "client/tienda/tienda.html",
        {"producto": pagina_producto, "contador_producto": contar_productos},
    )


# Tienda un producto unico hacia su detalle
def detalle_producto(request, categoria_slug, producto_slug):
    try:
        # Intenta obtener un único producto filtrando por el slug de la categoría y el slug del producto
        producto_unico = Producto.objects.get(
            categoria__slug=categoria_slug, slug=producto_slug
        )
    except Exception as e:
        raise e

    # filtramos si el usuario ya a comprado el producto
    if request.user.is_authenticated:
        try:
            pedido = Pedido.objects.filter(usuario=request.user, ordenado=True).exists()
        except Pedido.DoesNotExist:
            pedido = None
    else:
        pedido = None

    reviews = Valoraciones.objects.filter(producto_id=producto_unico.id, estado=True)

    return render(
        request,
        "client/tienda/detalle_producto.html",
        {
            "producto_unico": producto_unico,
            "review": reviews,
            "pedido": pedido,
        },
    )


def filtro_buscar_producto(request):
    palabra_busqueda = None
    contar_productos = 0
    if "txtBusqueda" in request.GET:
        # Si está presente, obtenemos el valor de la palabra clave de la solicitud GET
        txtBusqueda = request.GET["txtBusqueda"]
        # Verificamos si la palabra clave no está vacía
        if txtBusqueda:
            palabra_busqueda = Producto.objects.filter(
                Q(nombre__icontains=txtBusqueda) | Q(descripcion__icontains=txtBusqueda)
            )
            # Contador de productos encontrados
            contar_productos = palabra_busqueda.count()
            if contar_productos == 0:
                # messages.error(request, f"No se encontraron productos que coincidan con la palabra {txtBusqueda}")
                return render(
                    request,
                    "client/tienda/tienda.html",
                    {
                        "error_busqueda": f"No se encontraron productos que coincidan con la palabra {txtBusqueda}"
                    },
                )
    # El metodo va a la esta vista tienda.html. por que la vista del navbar.html es incluida en el HTML base, por lo tanto no tiene ruta
    return render(
        request,
        "client/tienda/tienda.html",
        {
            "producto": palabra_busqueda,
            "contador_producto": contar_productos,
            "txtBuscar": txtBusqueda,
        },
    )


# ? Corregir que el filtro pueda buscar con decimales
def filtro_rango_precios(request):
    try:
        # replace(".", "") es utilizado para la busqueda por punto eje: 1.000.000
        precio_minimo = float(request.POST.get("min_precio").replace(".", ""))
        precio_maximo = float(request.POST.get("max_precio").replace(".", ""))
    except ValueError:
        # messages.success(request, "Los valores ingresados deben ser numéricos")
        return render(
            request,
            "client/tienda/tienda.html",
            {"error_precio": "Los valores del precio son inválidos"},
        )
    productos = Producto.objects.filter(
        Q(precio__range=[precio_minimo, precio_maximo])
    ).order_by("precio")

    contar_productos = productos.count()
    if contar_productos == 0:
        return render(
            request,
            "client/tienda/tienda.html",
            {
                "error_busqueda":  f"No se encontraron productos dentro del rango de precios de {"{:,.0f}".format(precio_minimo).replace(',', '.')} a {"{:,.0f}".format(precio_maximo).replace(',', '.')}"            
            }
        )

    return render(
        request,
        "client/tienda/tienda.html",
        {"filtro_precio": productos, "contador_producto": contar_productos},
    )


@api_view(["POST"])
def range_priceAPIView(request):
    try:
        precio_minimo = float(request.GET.get("min_precio").replace(".", ""))
        precio_maximo = float(request.GET.get("max_precio").replace(".", ""))
    except ValueError:
        return Response(
            {"error": "Los valores de precio son inválidos"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if precio_minimo is not None and precio_maximo is not None:
        productos = Producto.objects.filter(
            Q(precio__range=[precio_minimo, precio_maximo])
        ).order_by("precio")
                        
        contar_productos = productos.count()
        if contar_productos == 0:
            return Response(
                {"error":  f"No se encontraron productos dentro del rango de precios de {"{:,.0f}".format(precio_minimo).replace(',', '.')} a {"{:,.0f}".format(precio_maximo).replace(',', '.')}"},status=status.HTTP_400_BAD_REQUEST
            )

    else:
        return Response(
            {"error": "Los valores de precio deben ser número"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ? Terminar
def valoracion(request, producto_id):
    # almacena la ruta anterior, para ser redirijidad
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        try:
            # ? __id una forma de acceder al id, del ese modelo
            valoracion = Valoraciones.objects.get(
                usuario__id=request.user.id, producto__id=producto_id
            )
            # Trear el formulario
            # pasamos una instanca si el usuario ya tiene una reseña, entonces para que pueda actualizar esa reseña
            form = ValoracionesForm(request.POST, instance=valoracion)
            form.save()
            messages.success(request, "Tu reseña ha sido actualizada")
            return redirect(url)
        except Valoraciones.DoesNotExist:
            form = ValoracionesForm(request.POST)
            if form.is_valid():
                data = Valoraciones()
                data.calificacion = form.cleaned_data["calificacion"]
                data.comentario = form.cleaned_data["comentario"]
                data.producto_id = producto_id
                data.usuario_id = request.user.id
                data.save()
                messages.success(request, "Tu reseña ha sido enviada")
                return redirect(url)


# ? APIS
@api_view(["GET"])
def categoryAPIView(request):
    queryset = Categoria.objects.all()
    serializer = CategoriaSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#  Me trae los productos de una categoría
@api_view(["GET"])
def storeAPIView(request, category_id=None):
    if category_id is not None:
        categorias = get_object_or_404(Categoria, id=category_id)
        productos = Producto.objects.all().filter(categoria=categorias, disponible=True)
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": "No se encontro el producto con la categoria"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# Detalle de un unico producto
@api_view(["GET"])
def detail_productAPIView(request, category_slug, product_slug):
    try:
        # Intenta obtener un único producto filtrando por el slug de la categoría y el slug del producto
        categoria = get_object_or_404(Categoria, slug=category_slug)
        producto = get_object_or_404(Producto, categoria=categoria, slug=product_slug)

        serializer = ProductoSerializer(producto)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Producto.DoesNotExist:
        return Response(
            {"error": "Lista de productos no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
def detail_productAPIView2(request, category_id, product_id):
    try:
        # Intenta obtener un único producto filtrando por el slug de la categoría y el slug del producto
        categoria = get_object_or_404(Categoria, id=category_id)
        producto = get_object_or_404(Producto, categoria=categoria, id=product_id)

        serializer = ProductoSerializer(producto)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Producto.DoesNotExist:
        return Response(
            {"error": "Lista de productos no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
def detail_productsAPIView(request, product_id):
    try:
        producto = get_object_or_404(Producto, id=product_id)

        serializer = ProductoSerializer(producto)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Producto.DoesNotExist:
        return Response(
            {"error": "Lista de productos no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )


# Buscador de un producto
@api_view(["POST"])
def searchProductAPIView(request):
    palabra_clave = None
    contar_productos = 0

    palabra_clave = request.GET.get("txtBusqueda")

    if palabra_clave:
        productos_encontrados = Producto.objects.filter(
            Q(nombre__icontains=palabra_clave) | Q(descripcion__icontains=palabra_clave)
        )

        contar_productos = productos_encontrados.count()
        if contar_productos == 0:
            return Response(
                {"error": "No se encontraron productos que coincidan con la búsqueda"},
                status=status.HTTP_404_NOT_FOUND,
            )

    # Serializar todos los productos encontrados, en caso de que no funcion crear un serializer para search product
    serializer = ProductoSerializer(productos_encontrados, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)





# ? Admin
# @login_required(login_url="inicio_sesion")
def agregar_productos(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto agregado")
            form = ProductoForm()
        else:
            messages.error(
                request,
                "Ha ocurrido un error en el formulario, intenta agregar otra vez el producto",
            )
    else:
        form = ProductoForm()
    return render(request, "admin/productos/form_producto.html", {"form": form})


@login_required(login_url="inicio_sesion")
def listar_productos(request):
    # Listar
    queryset = Producto.objects.all()

    # Agregar
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto guardado")
            form = ProductoForm()
        else:
            messages.error(
                request,
                "Ha ocurrido un error en el formulario, intenta agregar otra vez el producto",
            )
    else:
        form = ProductoForm()
    return render(
        request,
        "admin/productos/lista_producto.html",
        {"producto": queryset, "form": form},
    )


def detalle_producto_admin(request, id_producto):
    if request.method == "GET":
        detalle_producto = get_object_or_404(Producto, pk=id_producto)
        form = ProductoForm(instance=detalle_producto)
        return render(request, "admin/productos/detalle_producto.html",  {
            "detalle":detalle_producto, "form":form
        })
    
    else:
        try:
            # Actualizar
            detalle_producto = get_object_or_404(Producto, pk=id_producto)
            form = ProductoForm(request.POST,  request.FILES, instance=detalle_producto)
            form.save()
            messages.success(request, "Producto actualizado")
            return redirect("lista_productos")
        except:
            messages.error(request, "Ha ocurrido un error en el formulario, intenta actualizar otra vez el producto")
            return render(request, "admin/productos/detalle_producto.html", { "detalle":detalle_producto, "form":form})

# ! corregir
def eliminar_producto(request, id_producto):
    producto = get_object_or_404(Producto, id=id_producto)
    if request.method == "POST":
        producto.delete()
        messages.success(request,"Producto eliminado")
        return redirect("lista_productos")
    else:
        messages.error(request,"ERROR")
    
    


@login_required(login_url="inicio_sesion")
def lista_categorias(request):
    return render(request, "admin/categoria/lista_categoria.html")

from django.test import TestCase
from .forms import ProductoForm, CategoriaForm
from .models import  Categoria
from django.urls import reverse, resolve
from . import views
from django.test import SimpleTestCase


class ProductoFormTest(TestCase):
    def setUp(self):
        # Crea una categoría de prueba
        self.categoria = Categoria.objects.create(nombre="Categoría de prueba")

    def test_producto_form_invalid_data(self):
        form = ProductoForm(data={
            "nombre": "",  # Campo requerido
            "descripcion": "Descripción de prueba",
            "precio": 10.0,
            "stock": 50,
            "imagen": None,
            "categoria": self.categoria.id,
            "disponible": True
        })
        self.assertFalse(form.is_valid())

    def test_producto_form_blank_data(self):
        form = ProductoForm(data={})  # Envío de datos vacíos
        self.assertFalse(form.is_valid())


class CategoriaFormTest(TestCase):
    def test_categoria_form_valid_data(self):
        form = CategoriaForm(data={
            "nombre": "Categoria de prueba",
            "descuento": 10,
            "fecha_inicio": "2024-04-15T00:00",
            "fecha_fin": "2024-04-30T00:00"
        })
        self.assertTrue(form.is_valid())

    def test_categoria_form_invalid_data(self):
        form = CategoriaForm(data={
            "nombre": "",  # Campo requerido
            "descuento": -10,  # Debe ser un valor positivo
            "fecha_inicio": "2024-04-15T00:00",
            "fecha_fin": "2024-04-30T00:00"
        })
        self.assertFalse(form.is_valid())

    def test_categoria_form_blank_data(self):
        form = CategoriaForm(data={})  # Envío de datos vacíos
        self.assertFalse(form.is_valid())

class TestUrls(SimpleTestCase):
    def test_tienda_url_resolved(self):
        url = reverse('tienda')
        self.assertEqual(resolve(url).func, views.tienda)

    def test_categoria_a_producto_url_resolved(self):
        url = reverse('categoria_a_producto', args=['test-categoria'])
        self.assertEqual(resolve(url).func, views.tienda)

    def test_detalle_producto_url_resolved(self):
        url = reverse('detalle_producto', args=['test-categoria', 'test-producto'])
        self.assertEqual(resolve(url).func, views.detalle_producto)

    def test_buscar_producto_url_resolved(self):
        url = reverse('buscar_producto')
        self.assertEqual(resolve(url).func, views.filtro_buscar_producto)

    def test_filtro_precios_url_resolved(self):
        url = reverse('filtro_precios')
        self.assertEqual(resolve(url).func, views.filtro_rango_precios)


   
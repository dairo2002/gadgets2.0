from django.test import TestCase
from .forms import PedidoForm
from .models import Pedido

class PedidoFormTest(TestCase):
    # Este test valida si el formulario de pedido acepta datos válidos.
    def test_pedido_form_valid_data(self):
        form = PedidoForm(data={
            "nombre": "Juan",
            "apellido": "Perez",
            "correo_electronico": "juan@example.com",
            "telefono": "12345678",
            "direccion": "Calle 123",
            "direccion_local": "",
            "codigo_postal": "12345"
        })
        self.assertTrue(form.is_valid())
        
# Este test verifica si el formulario de pedido rechaza datos inválidos.
    def test_pedido_form_invalid_data(self):
        form = PedidoForm(data={
            "nombre": "Juan2",
            "apellido": "Perez3",
            "correo_electronico": "juan@example",
            "telefono": "1234567891011",
            "direccion": "C",
            "direccion_local": "",
            "codigo_postal": "abcde"
        })
        self.assertFalse(form.is_valid())

    def test_pedido_form_missing_data(self):
        form = PedidoForm(data={})  # Envío de datos vacíos
        self.assertFalse(form.is_valid())

   
    def test_pedido_form_invalid_email(self):
        # Prueba si el correo electrónico es válido
        form = PedidoForm(data={
            "nombre": "Juan",
            "apellido": "Perez",
            "correo_electronico": "invalid_email",
            "telefono": "12345678",
            "direccion": "Calle 123",
            "direccion_local": "",
            "codigo_postal": "12345"
        })
        self.assertFalse(form.is_valid())

class PedidoModelTest(TestCase):
    # Este test verifica si se puede crear un pedido correctamente utilizando el modelo `Pedido`.
    def test_pedido_model_creation(self):
        pedido = Pedido.objects.create(
            numero_pedido="123456",
            correo_electronico="juan@example.com",
            nombre="Juan",
            apellido="Perez",
            telefono="12345678",
            direccion="Calle 123",
            ordenado=False,
            departamento="Departamento",
            municipio="Municipio",
            codigo_postal="12345",
            total_pedido=100.00
        )
        self.assertIsInstance(pedido, Pedido)
        self.assertEqual(str(pedido), "Juan")

    def test_pedido_model_defaults(self):
        # Prueba si los valores predeterminados se establecen correctamente
        pedido = Pedido.objects.create(
            correo_electronico="juan@example.com",
            nombre="Juan",
            apellido="Perez",
            telefono="12345678",
            direccion="Calle 123",
            total_pedido=0  # Proporciona un valor para total_pedido
        )
        self.assertFalse(pedido.ordenado) 
        
    def test_pedido_model_negative_total(self):
        # Prueba si se puede crear un pedido con un total negativo
        pedido = Pedido.objects.create(
            correo_electronico="juan@example.com",
            nombre="Juan",
            apellido="Perez",
            telefono="12345678",
            direccion="Calle 123",
            total_pedido=-100.00
        )
        self.assertEqual(pedido.total_pedido, -100.00)

    def test_pedido_model_large_total(self):
        # Prueba si se puede crear un pedido con un total muy grande
        pedido = Pedido.objects.create(
            correo_electronico="juan@example.com",
            nombre="Juan",
            apellido="Perez",
            telefono="12345678",
            direccion="Calle 123",
            total_pedido=900000.00
        )
        self.assertEqual(pedido.total_pedido, 900000.00)

    

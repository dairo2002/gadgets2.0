from django.test import TestCase
from carrito.models import Carrito
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class CarritoModelTest(TestCase):
    def test_carrito_creado_correctamente(self):
        # Este test verifica si el carrito se crea correctamente en la base de datos.
        carrito = Carrito.objects.create()
        self.assertIsNotNone(carrito)

    @classmethod
    def setUpTestData(cls):
        # Configura datos de prueba para usar en las pruebas de modelos.
        cls.carrito = Carrito.objects.create(session_id='testsession123')

    def test_carrito_str(self):
        # Este test verifica si la representación en cadena del carrito es la esperada.
        carrito = Carrito.objects.get(id=self.carrito.id)
        self.assertEqual(str(carrito), f"Carrito de None - {carrito.id}")

    def test_carrito_usuario_null(self):
        # Este test verifica si el campo de usuario del carrito está vacío cuando se crea con una sesión.
        carrito = Carrito.objects.create(session_id='testsession456')
        self.assertIsNone(carrito.usuario)
        self.assertEqual(carrito.session_id, 'testsession456')


# Views
class TestCarritoAPI(TestCase):
    def setUp(self):
        # Configura el cliente para realizar solicitudes a la API.
        self.client = APIClient()

    def test_creacion_carrito(self):
        # Este test verifica si la vista de creación de carrito devuelve un código de estado HTTP 200 OK.
        url = reverse('mostrar_carrito')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mostrar_carrito(self):
        # Este test verifica si la vista de mostrar carrito devuelve un código de estado HTTP 200 OK.
        url = reverse('mostrar_carrito')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

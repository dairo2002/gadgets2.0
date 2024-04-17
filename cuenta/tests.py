# Pruebas pertinentes de Cuenta.
from django.test import TestCase
from cuenta.models import Cuenta
from django.contrib import admin
from cuenta.admin import CuentaAdmin
from .forms import RegistroForms, PerfilForms
from django.test import TestCase
from django.urls import reverse

# Pruebas pertinentes de Models.py
class CuentaModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Creamos usuario para realizar los test
        Cuenta.objects.create(
            nombre='John',
            apellido='Doe',
            username='johndoe',
            correo_electronico='john@example.com',
            telefono='123456789'
        )

    def test_nombre_completo(self):
        # Corroboramos si el método usuario_nombre_completo devuelve el nombre completo correctamente.
        cuenta = Cuenta.objects.get(id=1)
        nombre_completo_esperado = f"{cuenta.nombre} {cuenta.apellido}"
        self.assertEqual(cuenta.usuario_nombre_completo(), nombre_completo_esperado)

    def test_cuenta_str(self):
        # Verificamos si la representación de cadena de un objeto de "Cuenta" es igual a su dirección de correo electrónico.
        cuenta = Cuenta.objects.get(id=1)
        self.assertEqual(str(cuenta), cuenta.correo_electronico)

    def test_has_perm(self):
        # Se Verifica si el método "has_perm" devuelve True para un usuario administrador.
        cuenta = Cuenta.objects.get(id=1)
        cuenta.is_admin = True
        self.assertTrue(cuenta.has_perm(None))

    def test_has_module_perms(self):
        # Validamos si el método has_module_perms devuelve True para un usuario.
        cuenta = Cuenta.objects.get(id=1)
        self.assertTrue(cuenta.has_module_perms(None))

    def test_is_staff(self):
        # Se prueba si el atributo is_staff se establece correctamente para un usuario.
        cuenta = Cuenta.objects.get(id=1)
        self.assertFalse(cuenta.is_staff) 

    def test_is_active(self):
        # Aqui ponermos a prueba el atributo is_active si se establece correctamente para un usuario.
        cuenta = Cuenta.objects.get(id=1)
        self.assertFalse(cuenta.is_active)  # Por defecto, debería ser False

    def test_create_user(self):
        # Verificamos si se puede crear un usuario normal correctamente.
        usuario = Cuenta.objects.create_user(
            nombre='Alice',
            apellido='Smith',
            username='alicesmith',
            correo_electronico='alice@example.com',
            telefono='987654321',
            password='password123'
        )
        self.assertIsNotNone(usuario)

    def test_create_superuser(self):
        # Aqui verificamos la creacion de usuario con rol superusuario "superuser"
        superusuario = Cuenta.objects.create_superuser(
            nombre='Admin',
            apellido='User',
            username='adminuser',
            correo_electronico='admin@example.com',
            telefono='123456789',
            password='admin123'
        )
        self.assertTrue(superusuario.is_admin)
        self.assertTrue(superusuario.is_active)
        self.assertTrue(superusuario.is_staff)


# Pruebas pertinentes de admin.py
class TestCuentaAdmin(TestCase):
    def test_cuenta_admin_should_be_registered(self):
        # Verifica que el administrador de Cuenta esté registrado en el sitio de administración de Django.
        self.assertTrue(isinstance(admin.site._registry[Cuenta], CuentaAdmin))

    def test_cuenta_admin_should_set_list_display(self):
        # Verifica que el administrador de Cuenta tenga los campos definidos en 'list_display'.
        expected = (
            "correo_electronico",
            "nombre",
            "apellido",
            "username",
            "inicio_acceso",
            "ultimo_acceso",
            "is_active",
            "is_admin",
        )
        self.assertEqual(CuentaAdmin.list_display, expected)

    def test_cuenta_admin_should_set_list_display_links(self):
        # Verifica que el administrador de Cuenta tenga los campos definidos en 'list_display_links'.
        expected = ("correo_electronico", "username")
        self.assertEqual(CuentaAdmin.list_display_links, expected)

    def test_cuenta_admin_should_set_readonly_fields(self):
        # Verifica que el administrador de Cuenta tenga los campos definidos en 'readonly_fields'.
        expected = ("inicio_acceso", "ultimo_acceso")
        self.assertEqual(CuentaAdmin.readonly_fields, expected)

    def test_cuenta_admin_should_set_list_filter(self):
        # Verifica que el administrador de Cuenta tenga los campos definidos en 'list_filter'.
        expected = ["is_active"]
        self.assertEqual(CuentaAdmin.list_filter, expected)

    def test_cuenta_admin_should_set_search_fields(self):
        # Verifica que el administrador de Cuenta tenga los campos definidos en 'search_fields'.
        expected = ["nombre", "correo_electronico"]
        self.assertEqual(CuentaAdmin.search_fields, expected)

    def test_cuenta_admin_should_set_fieldsets_to_empty_tuple(self):
        # Verifica que el administrador de Cuenta tenga 'fieldsets' definido como una tupla vacía.
        self.assertEqual(CuentaAdmin.fieldsets, ())

class TestCuentaAdminSite(TestCase):
    def test_cuenta_admin_should_be_registered(self):
        # Verifica que el modelo de Cuenta esté registrado en el sitio de administración de Django.
        self.assertTrue(admin.site.is_registered(Cuenta))

#Pruebas de Tests.py

class RegistroFormsTest(TestCase):

    def test_valid_form(self):
        # Datos válidos para el formulario de registro
        form_data = {
            'nombre': 'John',
            'apellido': 'Doe',
            'correo_electronico': 'john@example.com',
            'telefono': '123456789',
            'password': 'Password123',
            'confirm_pwd': 'Password123'
        }
        form = RegistroForms(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_password(self):
        # Contraseña inválida: menos de 5 caracteres
        form_data = {
            'nombre': 'John',
            'apellido': 'Doe',
            'correo_electronico': 'john@example.com',
            'telefono': '123456789',
            'password': 'Pwd',
            'confirm_pwd': 'Pwd'
        }
        form = RegistroForms(data=form_data)
        self.assertFalse(form.is_valid())

    def test_password_mismatch(self):
        # Contraseñas no coinciden
        form_data = {
            'nombre': 'John',
            'apellido': 'Doe',
            'correo_electronico': 'john@example.com',
            'telefono': '123456789',
            'password': 'Password123',
            'confirm_pwd': 'DifferentPassword123'
        }
        form = RegistroForms(data=form_data)
        self.assertFalse(form.is_valid())

class PerfilFormsTest(TestCase):

    def test_valid_form(self):
        # Datos válidos para el formulario de perfil
        form_data = {
            'nombre': 'John',
            'apellido': 'Doe',
            'telefono': '123456789',
            'password': 'Password123',
            'confirm_pwd': 'Password123'
        }
        form = PerfilForms(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_password(self):
        # Contraseña inválida: menos de 5 caracteres
        form_data = {
            'nombre': 'John',
            'apellido': 'Doe',
            'telefono': '123456789',
            'password': 'Pwd',
            'confirm_pwd': 'Pwd'
        }
        form = PerfilForms(data=form_data)
        self.assertFalse(form.is_valid())

    def test_password_mismatch(self):
        # Contraseñas no coinciden
        form_data = {
            'nombre': 'John',
            'apellido': 'Doe',
            'telefono': '123456789',
            'password': 'Password123',
            'confirm_pwd': 'DifferentPassword123'
        }
        form = PerfilForms(data=form_data)
        self.assertFalse(form.is_valid())

#Test de views# Prueba del estado del código de la página de inicio de sesión.
class InicioSesionTestCase(TestCase):
    def test_inicio_sesion_status_code(self):
        # Obtiene la URL para la página de inicio de sesión.
        url = reverse('inicio_sesion')
        # Realiza una solicitud GET a la URL.
        response = self.client.get(url)
        # Comprueba si el código de estado de la respuesta es 200 (OK).
        self.assertEqual(response.status_code, 200)

# Pruebas de las vistas de la aplicación.
class PruebasVistas(TestCase):
    # Prueba de la vista de registro.
    def test_vista_registrarse(self):
        # Realiza una solicitud GET a la vista de registro.
        response = self.client.get(reverse('registrarse'))
        # Comprueba si el código de estado de la respuesta es 200 (OK).
        self.assertEqual(response.status_code, 200)

    # Prueba de la vista de inicio de sesión.
    def test_vista_inicio_sesion(self):
        # Realiza una solicitud GET a la vista de inicio de sesión.
        response = self.client.get(reverse('inicio_sesion'))
        # Comprueba si el código de estado de la respuesta es 200 (OK).
        self.assertEqual(response.status_code, 200)

    # Prueba de la vista de cierre de sesión.
    def test_vista_cerrar_sesion(self):
        # Realiza una solicitud GET a la vista de cierre de sesión.
        response = self.client.get(reverse('cerrar_sesion'))
        # Comprueba si el código de estado de la respuesta es 302 (Redirección temporal).
        self.assertEqual(response.status_code, 302)

    # Prueba de la vista del perfil de usuario.
    def test_vista_perfil(self):
        # Realiza una solicitud GET a la vista del perfil de usuario.
        response = self.client.get(reverse('perfil_usuario'))
        # Comprueba si el código de estado de la respuesta es 302 (Redirección temporal).
        self.assertEqual(response.status_code, 302)

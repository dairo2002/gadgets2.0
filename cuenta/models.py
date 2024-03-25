from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
    

from django.utils import timezone


class ManejardorCuenta(BaseUserManager):
    # Crear un usuario normal
    def create_user(
        self, nombre, apellido, username, correo_electronico, password=None
    ):
        if not correo_electronico:
            raise ValueError(
                "El usuario debe tener una dirección de correo electrónico"
            )
        if not username:
            raise ValueError("El usuario debe tener un nombre de usuario")

        # Crear un objeto de usuario
        user = self.model(
            # normalize_email Convierte la direccion de correo a minusculas y elimina espacios
            correo_electronico=self.normalize_email(correo_electronico),
            username=username,
            nombre=nombre,
            apellido=apellido,
        )

        # Establecer la contraseña y guardar el usuario en la base de datos
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Método para crear un superusuario, el administrador
    def create_superuser(
        self, nombre, apellido, username, correo_electronico, password
    ):
        # Utilizar el método create_user para crear un superusuario
        user = self.create_user(
            correo_electronico=self.normalize_email(correo_electronico),
            username=username,
            password=password,
            nombre=nombre,
            apellido=apellido,
        )

        # Establecer permisos y características especiales para el superusuario
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user


# Creamos el modelo de usuario personalizado que hereda de AbstractBaseUser
class Cuenta(AbstractBaseUser):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True, verbose_name="usuario")
    correo_electronico = models.EmailField(max_length=100, unique=True)
    telefono = models.CharField(max_length=12)

    # Permisos campos requeridos
    inicio_acceso = models.DateField(default=timezone.now)
    ultimo_acceso = models.DateField(default=timezone.now)
    # Falso se activa cuando creamos el usuario administrador
    is_staff = models.BooleanField(default=False, verbose_name="usuario")
    is_admin = models.BooleanField(default=False, verbose_name="Administrador")
    # Por defecto activo sea administrador o el usuario
    is_active = models.BooleanField(default=False, verbose_name="Actvio")

    # Campo con el que debe iniciar sesion el administrador
    USERNAME_FIELD = "correo_electronico"
    # Campos requeridos obligatorios ademas del correo y contraseña cuando se crea un usuario, atraves del comando createsuperuser
    REQUIRED_FIELDS = ["nombre", "apellido", "username"]
    # Utilizamos el manejador de usuarios personalizado
    objects = ManejardorCuenta()

    def __str__(self):
        return self.correo_electronico

    # Permiso para el administrador
    def has_perm(self, perm, obj=None):
        return  self.is_admin

    # Permisos a todos los modulos de la aplicacion
    def has_module_perms(self, add_label):
        return True    

    def usuario_nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


# ? Por ultimo, Configurar el modelo de cuenta de usuario en el settings.py para que sea establecido en admin

from django.db import models
from carrito.models import ItemCarrito
from cuenta.models import Cuenta
from tienda.models import Producto
from django.utils import timezone
from django.db.models import Q
from django.core.validators import EmailValidator
from django.core.validators import validate_image_file_extension
from django.core.validators import FileExtensionValidator


class Pago(models.Model):
    OPCIONES_ESTADO_PAGOS = [
        ("Verificacion", "Verificacion"),
        ("Aprobado", "Aprobado"),
        ("Rechazado", "Rechazado"),
    ]

    OPCIONES_ENVIO = [
        ("En espera de pago", "En espera de pago"),
        ("Enviado", "Enviado"),
        ("Rechazado", "Rechazado"),
        # Entregado
    ]

    usuario = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=50)
    cantidad_pagada = models.DecimalField(max_digits=12, decimal_places=2)
    comprobante = models.ImageField(
        upload_to="comprobantes/",
        validators=[validate_image_file_extension],
    )
    estado_pago = models.CharField(
        max_length=50, choices=OPCIONES_ESTADO_PAGOS, default="Verificacion"
    )
    estado_envio = models.CharField(
        max_length=50, choices=OPCIONES_ENVIO, default="En espera de pago"
    )
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.metodo_pago


class Pedido(models.Model):

    # null = acepta valores nulos
    # blank = Permite dejar el campo en blanco, opcional
    usuario = models.ForeignKey(Cuenta, on_delete=models.SET_NULL, null=True)
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, blank=True, null=True)
    numero_pedido = models.CharField(max_length=50)
    correo_electronico = models.EmailField(max_length=100)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    ordenado = models.BooleanField(default=False)
    direccion_local = models.CharField(max_length=50, blank=True)
    departamento = models.CharField(max_length=50)
    municipio = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=50)
    total_pedido = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.nombre

    def nombre_completo_pedido(self):
        return f"{self.nombre} {self.apellido}"

    def region(self):
        return f"{self.departamento}-{self.municipio}"

    def direccion_completa(self):
        return f"{self.direccion} {self.direccion_local}"


class Ventas(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    fecha = models.DateField(default=timezone.now)

    def __str__(self):
        return self.producto.nombre


class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)
    # departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    codigo_departamento = models.CharField(max_length=5)

    def __str__(self):
        return self.nombre




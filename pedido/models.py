from django.db import models
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
    OPCION_DEPARTAMENTO = [
        # 1, se almacena en la base de datos, 2 se muestra en la interfaz
        ("Amazonas", "Amazonas"),
        ("Antioquía", "Antioquía"),
        ("Huila", "Huila"),
    ]

    OPCION_CIUDADES = [
        ("Leticia", "Leticia"),
        ("Medellin", "Medellin"),
        ("Neiva", "Neiva"),
    ]

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
    departamento = models.CharField(max_length=50, choices=OPCION_DEPARTAMENTO)
    ciudad = models.CharField(max_length=50, choices=OPCION_CIUDADES)
    codigo_postal = models.CharField(max_length=50)
    total_pedido = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.nombre

    def nombre_completo_pedido(self):
        return f"{self.nombre} {self.apellido}"

    def region(self):
        return f"{self.ciudad}-{self.departamento}"

    def direccion_completa(self):
        return f"{self.direccion} {self.direccion_local}"

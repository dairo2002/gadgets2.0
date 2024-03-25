from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Cuenta


class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuenta
        fields = ["nombre", "apellido", "correo_electronico", "telefono", "password"]


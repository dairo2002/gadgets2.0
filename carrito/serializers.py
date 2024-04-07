from rest_framework import serializers
from .models import Carrito, ItemCarrito


class CarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrito
        fields = ["id", "usuario", "completed", "session_id"]

class ItemCarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCarrito
        fields = ["carrito", "producto", "cantidad"]
                
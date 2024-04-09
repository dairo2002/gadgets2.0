from rest_framework import serializers
from .models import Carrito, ItemCarrito


class ItemCarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCarrito
        fields = '__all__'

class CarritoSerializer(serializers.ModelSerializer):
    cartitems = ItemCarritoSerializer(many=True, read_only=True)

    class Meta:
        model = Carrito
        fields = '__all__'
                
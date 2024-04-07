from django.db import models
from tienda.models import Producto
from cuenta.models import Cuenta
import uuid
import locale, decimal


# Articulo del carrito
class Carrito(models.Model):
    # UUID, que es un identificador único universa, PK
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    usuario = models.OneToOneField(
        Cuenta, on_delete=models.CASCADE, null=True, blank=True
    )
    completed = models.BooleanField(default=False)
    session_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Carrito de {self.usuario} - {self.id}"


class ItemCarrito(models.Model):
    #  related_name='items' puedo acceder a los objecto de carrito con este nombre
    carrito = models.ForeignKey(
        Carrito, on_delete=models.CASCADE, related_name="cartitems"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="items"
    )    
    cantidad = models.IntegerField(default=1)
    # Otros campos de ItemCarrito

    def __str__(self):
        return f"Item de {self.producto.nombre} en {self.carrito}"

    def subtotal(self):
        return "{:,.0f}".format(self.operacion()).replace(",", ".")

    def operacion(self):
        if self.producto.aplicar_descuento():
            return self.producto.aplicar_descuento() * self.cantidad
        else:
            return self.producto.precio * self.cantidad

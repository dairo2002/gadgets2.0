from rest_framework import serializers
from .models import Pedido, Municipio, Departamento, HistorialPedidos, Pago
from django.core.files.base import ContentFile
import base64


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = [
            "metodo_pago",
            "comprobante",
        ]



class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = [
            "nombre",
            "apellido",
            "correo_electronico",
            "telefono",
            "direccion",
            "direccion_local",
            "departamento",
            "municipio",
            "codigo_postal",
        ]
           
class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = ['nombre', 'codigo']
        
        
class MunicipioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = ['nombre', 'codigo', 'codigo_departamento']



# ! Corregir que fue lo que hice aca.
class HistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialPedidos
        fields = ['nombre', 'codigo', 'codigo_departamento']

        
    '''
        pago = models.ForeignKey(Pago, on_delete=models.CASCADE, blank=True, null=True)   
        producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
        pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
        cantidad = models.IntegerField()
    '''
        
        
        # municipios = MunicipioSerializer(many=True, read_only=True)
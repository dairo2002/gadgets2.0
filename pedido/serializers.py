from rest_framework import serializers
from .models import Pedido, Municipio, Departamento

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


        
        # municipios = MunicipioSerializer(many=True, read_only=True)
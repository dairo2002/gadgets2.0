from django import forms
from .models import Producto, Categoria


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "descripcion",
            "precio",
            "stock",
            "imagen",
            "categoria",
            "disponible",
        ]
        labels = {
            "descripcion": "Descripción",
            "categoria": "Categoría",
        }

    def __init__(self, *args, **kwargs):
        super(ProductoForm, self).__init__(*args, **kwargs)
        self.fields["nombre"].widget.attrs.update(
            {"placeholder": "Nombre del producto"}
        )
        self.fields["descripcion"].widget.attrs.update(
            {"placeholder": "Descripción del producto", "rows": 3}
        )
        self.fields["precio"].widget.attrs.update(
            {"placeholder": "Precio del producto", "min": 0}
        )
        self.fields["stock"].widget.attrs.update(
            {"placeholder": "Stock del producto", "min": 0}
        )
        self.fields["imagen"].widget.attrs
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

        self.fields["categoria"].widget.attrs.update({"class": "form-select"})
        self.fields["categoria"].choices = [("", "Selecciona una categoría")] + list(
            Categoria.objects.values_list("id", "nombre")
        )
        self.fields["disponible"].widget.attrs["class"] = "form-check-input"


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = [
            "nombre",            
            "descuento",
            "fecha_inicio",
            "fecha_fin"
        ]
 
    def __init__(self, *args, **kwargs):
        super(CategoriaForm, self).__init__(*args, **kwargs)
        self.fields["nombre"].widget.attrs.update(
            {"placeholder": "Nombre de la categoria "}
        )
        self.fields["descuento"].widget.attrs.update(
            {"placeholder": "Ingrese el porcentaje del descuento", "min": 0}
        )
        self.fields["fecha_inicio"].widget =forms.DateTimeInput(
         attrs={'type':'datetime-local'}
        )

        self.fields["fecha_fin"].widget=forms.DateTimeInput(
         attrs={'type':'datetime-local'}
        )

      
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"




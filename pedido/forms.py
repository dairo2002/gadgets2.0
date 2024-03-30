from django import forms
from .models import Pedido, Pago


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            "nombre",
            "apellido",
            "correo_electronico",
            "telefono",
            "direccion",
            "direccion_local",
            "codigo_postal",
        ]

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        errores = []

        if any(char.isdigit() for char in nombre):
            errores.append("El nombre no puede tener números")

        if len(nombre) < 3 or len(nombre) > 15:
            errores.append("El nombre debe tener entre 3 y 15 caracteres")
        
        if errores:
            raise forms.ValidationError(errores)

        return nombre

    def clean_apellido(self):
        nombre = self.cleaned_data.get("apellido")
        errores = []

        if any(char.isdigit() for char in nombre):
            errores.append("El apellido no puede tener números")

        if len(nombre) < 3 or len(nombre) > 15:
            errores.append("El apellido debe tener entre 3 y 15 caracteres")

        if errores:
            raise forms.ValidationError(errores)

        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        errores = []

        if not telefono.isdigit():
            errores.append("El teléfono debe tener solo números")

        if len(telefono) < 8 or len(telefono) > 10:
            errores.append("El número de teléfono debe tener entre 8 y 10 dígitos")

        if errores:
            raise forms.ValidationError(errores)

        return telefono

    def __init__(self, *args, **kwargs):
        super(PedidoForm, self).__init__(*args, **kwargs)
        self.fields["nombre"].widget.attrs["placeholder"] = "Nombre"
        self.fields["apellido"].widget.attrs["placeholder"] = "Apellido"
        self.fields["correo_electronico"].widget.attrs[
            "placeholder"
        ] = "Dirección correo electrónico"
        self.fields["telefono"].widget.attrs["placeholder"] = "Numero telefónico"
        self.fields["direccion"].widget.attrs["placeholder"] = "Dirección"
        self.fields["direccion_local"].widget.attrs[
            "placeholder"
        ] = "Casa,apartamento,etc.(opcional)"
        self.fields["direccion_local"].widget.attrs["id"] = "txtDireccionLocal"
        self.fields["direccion_local"].widget.attrs["style"] = "display:none;"
        # self.fields["departamento"].widget.attrs["placeholder"] = "Elige"
        # self.fields["ciudad"].widget.attrs["placeholder"] = "Elige"
        self.fields["codigo_postal"].widget.attrs[
            "style"
        ] = "text-transform: uppercase;"

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class PagoForm(forms.ModelForm):
    metodo_pago = forms.ChoiceField(
        choices=(
            ("Efectivo", "Efectivo"),
            ("Nequi", "Nequi"),
        ),
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Pago
        fields = [
            "metodo_pago",
            "comprobante",
        ]

    def __init__(self, *args, **kwargs):
        super(PagoForm, self).__init__(*args, **kwargs)
        # Agregar clases de Bootstrap a los campos
        self.fields["comprobante"].widget.attrs["class"] = "form-control"

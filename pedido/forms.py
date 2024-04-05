from django import forms
from .models import Pedido, Pago, Ventas


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
        self.fields["codigo_postal"].widget.attrs[
            "style"
        ] = "text-transform: uppercase;"

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class PedidoFormA(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            "usuario",
            "nombre",
            "apellido",
            "correo_electronico",
            "numero_pedido",
            "telefono",
            "direccion",
            "direccion_local",
            "departamento",
            "municipio",
            "codigo_postal",
            "total_pedido",
            "pago",
            "ordenado",
        ]

    def __init__(self, *args, **kwargs):
        super(PedidoFormA, self).__init__(*args, **kwargs)
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

        self.fields["numero_pedido"].widget.attrs.update(
            {"placeholder": "Número de pedido", "min": 0}
        )

        self.fields["departamento"].widget.attrs.update({"placeholder": "Departamento"})

        self.fields["total_pedido"].widget.attrs.update(
            {"placeholder": "Total del pedido", "min": 0}
        )

        self.fields["pago"].widget.attrs.update({"placeholder": "Pagos", "min": 0})

        self.fields["usuario"].widget.attrs.update({"placeholder": "Nombre de Usuario"})

        self.fields["municipio"].widget.attrs.update(
            {"placeholder": "Nombre del municipio"}
        )

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

            self.fields["ordenado"].widget.attrs["class"] = "form-check-input"


class VentaForms(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = [
            "producto",
            "cantidad",
            "precio",
            "pedido",
            "pago",
            "usuario",
            "fecha",
        ]

    def __init__(self, *args, **kwargs):
        super(VentaForms, self).__init__(*args, **kwargs)

        self.fields["producto"].widget.attrs.update(
            {"placeholder": "Ingrese el producto", "min": 0}
        )

        self.fields["cantidad"].widget.attrs.update(
            {"placeholder": "Ingrese la cantidad", "min": 0}
        )

        self.fields["precio"].widget.attrs.update(
            {"placeholder": "Ingrese el precio", "min": 0}
        )

        self.fields["pedido"].widget.attrs.update({"placeholder": "Pedido"})

        self.fields["pago"].widget.attrs.update({"placeholder": "Pago"})

        self.fields["usuario"].widget.attrs.update(
            {"placeholder": "Ingrese el usuario"}
        )

        self.fields["fecha"].widget = forms.DateInput(attrs={"type": "date-local"})

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class PagosForms(forms.ModelForm):
    class Meta:
        model = Pago
        fields = [
            "metodo_pago",
            "cantidad_pagada",
            "estado_pago",
            "estado_envio",
            "usuario",
            "comprobante",
            "fecha",
        ]

    def __init__(self, *args, **kwargs):
        super(PagosForms, self).__init__(*args, **kwargs)

        self.fields["metodo_pago"].widget.attrs.update(
            {"placeholder": "Ingrese el metodo de pago"}
        )

        self.fields["cantidad_pagada"].widget.attrs.update(
            {"placeholder": "Ingrese la cantidad", "min": 0}
        )

        self.fields["estado_pago"].widget.attrs.update(
            {"placeholder": "Estado de pago", "min": 0}
        )

        self.fields["estado_envio"].widget.attrs.update(
            {"placeholder": "Estado de envío"}
        )

        self.fields["usuario"].widget.attrs.update({"placeholder": "Ingresa usuario"})

        self.fields["comprobante"].widget.attrs.update(
            {
                "placeholder": "Seleccione un comprobante",
                "accept": "image/*",  # Esto limitará la selección de archivos a imágenes
            }
        )

        self.fields["fecha"].widget = forms.DateTimeInput(
            attrs={"type": "datetime-local"}
        )

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class PagoForm(forms.ModelForm):
    OPCIONES_CHOICES = (("Efectivo", "Efectivo"), ("Nequi", "Nequi"))

    metodo_pago = forms.ChoiceField(choices=OPCIONES_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Pago
        fields = [
            "metodo_pago",
            "comprobante",
        ]

    def __init__(self, *args, **kwargs):
        super(PagoForm, self).__init__(*args, **kwargs)
        self.fields["comprobante"].widget.attrs["class"] = "form-control"

import re
from django import forms
from .models import Cuenta


class RegistroForms(forms.ModelForm):
    # Se crean estos campos que no estan en el modelo
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Ingresar contraseña"}),
    )

    confirm_pwd = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirmar contraseña"}),
    )

    class Meta:
        model = Cuenta
        # Traemos los campos del modelo de cuenta, que son aplicados al formulario,
        fields = ["nombre", "apellido", "correo_electronico", "telefono", "password"]

        labels = {
            "telefono": "Teléfono",
            "correo_electronico": "Correo electrónico",
        }

    # Funcion clean() validar campos
    def clean_confirm_pwd(self):
        cleaned_data = super(RegistroForms, self).clean()

        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirm_pwd")

        print(f"Registro: password {password} confirmar_password: {confirmar_password}")

        if password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden")

        if (
            len(password) < 5
            or len(password) > 12
            and len(confirmar_password) < 5
            or len(confirmar_password) > 12
        ):
            raise forms.ValidationError(
                "Las contraseña debe tener de 5 a 12 caracteres"
            )
        
        if not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', confirmar_password):
            raise forms.ValidationError("La contraseña debe contener al menos una letra y un número")

        return password

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")

        if any(char.isdigit() for char in nombre):
            raise forms.ValidationError("El nombre no puede tener números")

        if len(nombre) < 3 or len(nombre) > 15:
            raise forms.ValidationError("El nombre debe tener entre 3 y 15 caracteres")

        return nombre

    def clean_apellido(self):
        nombre = self.cleaned_data.get("apellido")

        if any(char.isdigit() for char in nombre):
            raise forms.ValidationError("El apellido no puede tener números")

        if len(nombre) < 3 or len(nombre) > 15:
            raise forms.ValidationError(
                "El apellido debe tener entre 3 y 15 caracteres"
            )

        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")

        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono debe tener solo números")

        if len(telefono) < 8 or len(telefono) > 10:
            raise forms.ValidationError(
                "El número de teléfono debe tener entre 8 y 10 dígitos"
            )

        return telefono
    
        



    def __init__(self, *args, **kwargs):
        super(RegistroForms, self).__init__(*args, **kwargs)
        self.fields["nombre"].widget.attrs["placeholder"] = "Ingrese su nombre"
        self.fields["apellido"].widget.attrs["placeholder"] = "Ingrese su apellido"
        self.fields["correo_electronico"].widget.attrs[
            "placeholder"
        ] = "Dirección correo electrónico"
        self.fields["telefono"].widget.attrs["placeholder"] = "Número telefónico"

        # Se itera para que cada campo tenga la misma clase
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"




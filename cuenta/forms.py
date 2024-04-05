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
        errores = []

        print(f"Registro: password {password} confirmar_password: {confirmar_password}")

        if password != confirmar_password:
            errores.append("Las contraseñas no coinciden")

        if (
            len(password) < 5
            or len(password) > 12
            and len(confirmar_password) < 5
            or len(confirmar_password) > 12
        ):
            errores.append("Las contraseña debe tener de 5 a 12 caracteres")

        if not re.search(r"\d", password) or not re.search(
            r"[a-zA-Z]", confirmar_password
        ):
            errores.append("La contraseña debe contener al menos una letra y un número")

        if errores:
            raise forms.ValidationError(errores)

        return password

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


class CuentaForms(forms.ModelForm):
    class Meta:

        password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Ingresar contraseña"}),
    )

        model = Cuenta
        # Traemos los campos del modelo de cuenta, que son aplicados al formulario,
        fields = ["nombre", "apellido" ,"username" ,"correo_electronico", "telefono", "password", "is_staff", "is_admin", "is_active"]

        labels = {
            "telefono": "Teléfono",
            "correo_electronico": "Correo electrónico",
            "is_staff": "Usuario",
            "is_admin": "Administrador",
            "is_active": "Activo",
            "username" : "Usuario",
            "password":"Contraseña"
        }
    
    def __init__(self, *args, **kwargs):
        super(CuentaForms, self).__init__(*args, **kwargs)
        self.fields["nombre"].widget.attrs["placeholder"] = "Ingrese su nombre"
        self.fields["apellido"].widget.attrs["placeholder"] = "Ingrese su apellido"
        self.fields["correo_electronico"].widget.attrs[
            "placeholder"
        ] = "Dirección correo electrónico"
        self.fields["telefono"].widget.attrs["placeholder"] = "Número telefónico"
        self.fields["username"].widget.attrs["placeholder"] = "Ingrese su nombre de usuario"
        # self.fields["password"].widget.attrs["placeholder"] = "Ingrese su contraseña"
        
        """self.fields["ultimo_acceso"].widget =forms.DateTimeInput(
         attrs={'type':'datetime-local'}
            )
        self.fields["inicio_acceso"].widget =forms.DateTimeInput(
         attrs={'type':'datetime-local'}
        )"""


        # Se itera para que cada campo tenga la misma clase
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
        
        self.fields["is_staff"].widget.attrs["class"] = "form-check-input"
        self.fields["is_admin"].widget.attrs["class"] = "form-check-input"
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"

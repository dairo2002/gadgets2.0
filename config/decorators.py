

from django.shortcuts import redirect
from cuenta.models import Cuenta


def protect_route(view_func):
    def wrapper(request, *args, **kwargs):
        cuenta = Cuenta.objects.get(correo_electronico=request.user)    
        if cuenta.is_active and cuenta.is_staff and cuenta.is_admin:
            return view_func(request, *args, **kwargs)
        else:
            return redirect("inicio_sesion")
    return wrapper
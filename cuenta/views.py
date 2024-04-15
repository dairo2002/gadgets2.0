from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RegistroForms, CuentaForms, PerfilForms
from config.decorators import protect_route
from django.contrib import auth, messages
from .models import Cuenta

# importaciones email
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from datetime import datetime, timedelta
from carrito.models import Carrito, ItemCarrito
from django.utils import timezone

# API
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import CuentaSerializer, PerfilSerializer
from rest_framework.views import APIView
from rest_framework import status

import pdb


def registrarse(request):
    if request.method == "POST":
        formulario = RegistroForms(request.POST)
        if formulario.is_valid():
            nombre = formulario.cleaned_data["nombre"]
            apellido = formulario.cleaned_data["apellido"]
            correo_electronico = formulario.cleaned_data["correo_electronico"]
            telefono = formulario.cleaned_data["telefono"]
            password = formulario.cleaned_data["password"]

            # Toma la dirección de correo electrónico y extrae el como nombre de usuario lo que antes símbolo "@", con esto tambien evitamos repetidos
            usuario = correo_electronico.split("@")[0]

            if Cuenta.objects.filter(username=usuario).exists():
                messages.warning(request, "El nombre de usuario ya existe")
                return redirect("registrarse")

            # metodo create_user creado en ManejadorCuenta
            crear_usuario = Cuenta.objects.create_user(
                nombre=nombre,
                apellido=apellido,
                correo_electronico=correo_electronico,
                username=usuario,
                password=password,
            )

            # El campo de telefono es guardado de esta forma porque es un campo obligatorio
            crear_usuario.telefono = telefono
            crear_usuario.save()

            # Informacion enviada al correo del usuario
            current_site = get_current_site(request)
            mail_subject = "Activar cuenta con Gadgets Future"
            mensaje = render_to_string(
                "client/cuenta/activar_cuenta.html",
                {
                    "usuario": crear_usuario,
                    "dominio": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(crear_usuario.id)),
                    "token": default_token_generator.make_token(crear_usuario),
                    "expiracion": timezone.now() + timedelta(hours=1),
                },
            )

            to_email = correo_electronico
            # EmailMessage
            send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
            send_email.attach_alternative(mensaje, "text/html")
            send_email.send()

            messages.warning(
                request,
                "Por favor activa la cuenta ingresando al enlace enviado al correo electrónico",
            )
            # ruta de gmail que lo redirije a iniciar sesion
            return redirect(
                "/cuenta/inicio_sesion/?command=verificacion&email="
                + correo_electronico
            )
    else:
        formulario = RegistroForms()
    return render(request, "client/cuenta/registrarse.html", {"form": formulario})


def activar_cuenta(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        usuario = Cuenta._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Cuenta.DoesNotExist):
        usuario = None

    if usuario is not None:
        if default_token_generator.check_token(usuario, token):
            usuario.is_active = True
            usuario.is_staff = True
            usuario.save()
            messages.success(request, "Felicidades! Tu cuenta está activada")
            return redirect("inicio_sesion")
    else:
        messages.error(request, "El enlace para activar la cuenta ha caducado.")
        return redirect("registrarse")


def inicio_sesion(request):
    # if request.user.is_authenticated:
    #     return redirect("index")

    # Verifica si la solicitud al servidor es de tipo POST
    if request.method == "POST":
        correo_electronico = request.POST["correo_electronico"]
        password = request.POST["password"]
        usuarios = auth.authenticate(
            correo_electronico=correo_electronico, password=password
        )

        if usuarios is not None:
            if usuarios.is_active:
                if usuarios.is_admin and usuarios.is_staff:
                    auth.login(request, usuarios)
                    messages.success(
                        request, f"Bienvenido {usuarios.nombre} {usuarios.apellido}"
                    )
                    return redirect("dashboard")
                elif usuarios.is_staff:
                    auth.login(request, usuarios)
                    messages.success(
                        request, f"Bienvenido {usuarios.nombre} {usuarios.apellido}"
                    )

                    if "nonuser" in request.session:
                        try:
                            cartNoneUser = Carrito.objects.get(session_id=request.session["nonuser"], completed=False)
                            items_non_user = ItemCarrito.objects.filter(carrito=cartNoneUser)
                            if items_non_user:
                                if request.user.is_authenticated:
                                    cart_user, created = Carrito.objects.get_or_create(usuario=request.user, completed=False)
                                    for item_non_user in items_non_user:
                                        # Verificar si el producto ya está en el carrito del usuario autenticado
                                        existing_item = ItemCarrito.objects.filter(carrito=cart_user, producto=item_non_user.producto).first()
                                        if existing_item:
                                            existing_item.cantidad += item_non_user.cantidad
                                            existing_item.save()
                                        else:
                                            # Crea un nuevo ItemCarrito asociado al carrito del usuario autenticado
                                            nuevo_item = ItemCarrito.objects.create(carrito=cart_user, producto=item_non_user.producto, cantidad=item_non_user.cantidad)
                                # Elimina el carrito del usuario no autenticado
                                cartNoneUser.delete()
                        except Exception as e:
                            print("Error al transferir productos:", e)
                            pass
                    return redirect("index")
            else:
                messages.error(request, "Tu cuenta está desactivada.")
        else:
            messages.error(request, "Credenciales incorrectas")
            return redirect("inicio_sesion")
    return render(request, "client/cuenta/inicio_sesion.html")


@login_required(login_url="inicio_sesion")
def perfil(request):
    usuario_actual=request.user    
    if request.method == "POST":
        formulario = PerfilForms(request.POST)
        if formulario.is_valid():
            nombre = formulario.cleaned_data["nombre"]
            apellido = formulario.cleaned_data["apellido"]            
            telefono = formulario.cleaned_data["telefono"]
            password = formulario.cleaned_data["password"]                                                                        
        
            cuenta = Cuenta.objects.get(pk=usuario_actual.pk)        
            cuenta.nombre=nombre
            cuenta.apellido=apellido                                
            cuenta.telefono=telefono
            cuenta.password=password
            # Se verifica si se ingreso una nueva contraseña
            if password:
                cuenta.set_password(password)
            cuenta.save()
            messages.success(request, 'Perfil actualizado correctamente, Inicia sesión nuevamente')
            return redirect("inicio_sesion")
        else:                                                                              
            messages.error(request, 'Ha ocurrido un error al actualizar tu perfil, revisa el formulario otra vez')        
    else:
        datos_usuario = {
            "nombre": usuario_actual.nombre,
            "apellido": usuario_actual.apellido,            
            "telefono": usuario_actual.telefono,
        }
        formulario = PerfilForms(initial=datos_usuario)
        
    return render(request, "client/cuenta/perfil_usuario.html", {"form": formulario,  "usuario":usuario_actual})


@login_required(login_url="inicio_sesion")
def cerrar_sesion(request):
    auth.logout(request)
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect("inicio_sesion")


@login_required(login_url="inicio_sesion")
def desactivar_cuenta(request):
    cuenta = Cuenta.objects.get(correo_electronico=request.user)
    if request.method == "POST":
        cuenta.is_active = False
        cuenta.is_staff = False
        cuenta.is_admin = False
        cuenta.save()
        # Cerramos la sesión
        auth.logout(request)
        messages.success(request, "Tu cuenta ha sido desactivada")
    else:
        messages.error(request, "Ha ocurrido un error")
    return redirect("index")


def recuperar_password(request):
    if request.method == "POST":
        correo_electronico = request.POST["correo_electronico"]
        if Cuenta.objects.filter(correo_electronico=correo_electronico).exists():
            usuario = Cuenta.objects.get(correo_electronico__exact=correo_electronico)

            current_site = get_current_site(request)
            mail_subject = "Recuperar contraseña"
            mensaje = render_to_string(
                "client/cuenta/mensaje_cambiar_pwd.html",
                {
                    "usuario": usuario,
                    "dominio": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(usuario.pk)),
                    "token": default_token_generator.make_token(usuario),
                },
            )

            to_email = correo_electronico
            send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
            send_email.attach_alternative(mensaje, "text/html")
            send_email.send()

            messages.success(
                request,
                "Te enviamos un correo electrónico de restablecimiento de contraseña",
            )
            return redirect("inicio_sesion")
        else:
            messages.error(request, "La cuenta no existe!")
            return redirect("recuperar_password")
    return render(request, "client/cuenta/recuperar_password.html")


def enlace_cambiar_pwd(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Cuenta._default_manager.get(id=uid)
    except (TypeError, ValueError, OverflowError, Cuenta.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Por favor restablecer la contraseña")
        return redirect("restablecer_password")
    else:
        messages.error(
            request,
            "El enlace para recuperar la contraseña ha caducado. Por favor, solicita un nuevo enlace.",
        )
        return redirect("inicio_sesion")


def restablecer_password(request):
    if request.method == "POST":
        new_password = request.POST["nueva_password"]
        confirm_password = request.POST["confirmar_password"]

        if new_password == confirm_password:
            uid = request.session.get("uid")
            user = Cuenta.objects.get(id=uid)
            user.set_password(new_password)
            user.save()
            messages.success(
                request,
                "Tu contraseña ha sido guardada, prueba iniciar sesión con tu nueva contraseña",
            )
            return redirect("inicio_sesion")
        else:
            messages.error(request, "Las contraseñas no coniciden")
            return redirect("restablecer_password")
    else:
        return render(request, "client/cuenta/restablecer_password.html")


# ? APIS
@api_view(["POST"])
def signup(request):
    serializer = CuentaSerializer(data=request.data)
    if serializer.is_valid():
        nombre = serializer.validated_data.get("nombre")
        apellido = serializer.validated_data.get("apellido")
        correo_electronico = serializer.validated_data.get("correo_electronico")
        telefono = serializer.validated_data.get("telefono")
        password = serializer.validated_data.get("password")
        usuario = correo_electronico.split("@")[0]

        if Cuenta.objects.filter(username=usuario).exists():
            return Response(
                {"error": "El nombre de usuario ya está en uso."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Utiliza tu método personalizado create_user para crear el usuario
        crear_usuario = Cuenta.objects.create_user(
            nombre=nombre,
            apellido=apellido,
            username=usuario,
            correo_electronico=correo_electronico,
            password=password,
        )
        crear_usuario.telefono = telefono
        crear_usuario.save()        
        
        current_site = get_current_site(request)
        mail_subject = "Activar cuenta con Gadgets Future"
        mensaje = render_to_string(
            "client/cuenta/activar_cuenta.html",
            {
                "usuario": crear_usuario,
                "dominio": current_site,
                "uid": urlsafe_base64_encode(force_bytes(crear_usuario.id)),
                "token": default_token_generator.make_token(crear_usuario),
                "expiracion": timezone.now() + timedelta(hours=1),
            },
        )

        to_email = correo_electronico    
        send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
        send_email.attach_alternative(mensaje, "text/html")
        send_email.send()
        # ruta de gmail que lo redirije a iniciar sesion
        # return redirect(
        #     "/cuenta/inicio_sesion/?command=verificacion&email=" + correo_electronico
        # )
        return Response(
            {
                "success": True,
                "message": "Por favor activa la cuenta ingresando al enlace enviado al correo electrónico",
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def login(request):
    if request.method == "POST":
        correo_electronico = request.data.get("correo_electronico")
        password = request.data.get("password")
        usuario = auth.authenticate(
            correo_electronico=correo_electronico, password=password
        )
        if usuario is not None:
            token = RefreshToken.for_user(usuario)
            return Response(
                {
                    "token": str(token.access_token),
                    # "actualizar ": str(token),
                    "success": True,
                    "message": f"Bienvenido {usuario.nombre} {usuario.apellido}",
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Usuario no autenticado
            return Response(
                {"error": True, "message": "Las credenciales son incorrectas"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    else:
        return Response(
            {"error": False, "message": "Método no permitido"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ? 2 formas de actualizar el perfil de un usuario

'''
Api perfil

Se maneja dos metodos primero se consulta los datos del usuario y despues se actualizan 
GET=consulta 
PUT=Actualiza 
'''

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def perfil_api(request):
    usuario_actual = request.user
    if request.method == "GET":
        datos_usuario = {
            "nombre": usuario_actual.nombre,
            "apellido": usuario_actual.apellido,
            "telefono": usuario_actual.telefono,
        }
        return Response(datos_usuario)
    elif request.method == "PUT":
        # Copia los datos de la solicitud
        datos = request.data.copy()
        # Encripta la contraseña si está presente en los datos
        if 'password' in datos:
            datos['password'] = make_password(datos['password'])
        # Utiliza el serializador para validar y guardar los datos
        formulario = PerfilSerializer(instance=usuario_actual, data=datos) 
        if formulario.is_valid():
            formulario.save()
            return Response({"message": "Perfil actualizado correctamente"}, status=status.HTTP_204_NO_CONTENT)           
        else:            
            return Response({"message": "Ha ocurrido un error al actualizar el perfil"}, formulario.errors, status=status.HTTP_400_BAD_REQUEST)



'''
APIS Perfil, otra forma por separado

- get_profile = Primero se puede consultar los datos del usuario, y se muestran
- put_profile = Segundo se llama la api de actualizar los datos en el formario

'''

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    usuario_actual = request.user
    datos_usuario = {
        "nombre": usuario_actual.nombre,
        "apellido": usuario_actual.apellido,
        "telefono": usuario_actual.telefono,
    }
    return Response(datos_usuario)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def put_profile(request):
    usuario_actual = request.user
    datos = request.data.copy()
    if 'password' in datos:
        datos['password'] = make_password(datos['password'])
    formulario = PerfilSerializer(instance=usuario_actual, data=datos) 
    if formulario.is_valid():
        formulario.save()
        return Response({"message": "Perfil actualizado correctamente"}, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({"message": "Ha ocurrido un error al actualizar el perfil"}, formulario.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout(request):
    # Cierra la sesión del usuario
    auth.logout(request)
    return Response({"success": True, "message": "Sesión cerrada exitosamente."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logoutV2(request):
    auth.logout(request)
    return Response({"success": True, "message": "Sesión cerrada exitosamente."})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deactivate_account(request):    
    if request.method == "POST":
        if request.user.is_authenticated:
            usuario = request.user
            usuario.is_active = False
            usuario.is_staff = False
            usuario.is_admin = False
            usuario.save()
            # Cerramos la sesión
            auth.logout(request)
            return Response(
                {"message": "Tu cuenta ha sido desactivada"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "No se puedo encontrar la cuenta"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        return Response(
            {"message": "Método no permitido"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def recover_password(request):
    if request.method == "POST":
        correo_electronico = request.data.get("correo_electronico")
        existe_email = Cuenta.objects.filter(
            correo_electronico=correo_electronico
        ).exists()
        if existe_email:

            usuario = Cuenta.objects.get(correo_electronico__exact=correo_electronico)

            current_site = get_current_site(request)
            mail_subject = "Recuperar contraseña"
            mensaje = render_to_string(
                "client/cuenta/mensaje_cambiar_pwd.html",
                {
                    "usuario": usuario,
                    "dominio": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(usuario.pk)),
                    "token": default_token_generator.make_token(usuario),
                    # "token": token_con_expiracion,
                },
            )

            # Configurar y enviar el correo electrónico
            to_email = correo_electronico
            send_email = EmailMultiAlternatives(mail_subject, mensaje, to=[to_email])
            send_email.attach_alternative(mensaje, "text/html")
            send_email.send()

            return Response(
                {
                    "message": "Se ha enviado un correo electrónico de restablecimiento de contraseña a su dirección de correo electrónico"
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "La cuenta no existe!"}, status=status.HTTP_400_BAD_REQUEST
            )


# ? ADMIN
@login_required(login_url="inicio_sesion")
@protect_route
def listar_usuario(request):
    queryset = Cuenta.objects.all()

    # Agregar
    if request.method == "POST":
        form = CuentaForms(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario guardada")
            form = CuentaForms()
        else:
            messages.error(
                request,
                "Ha ocurrido un error en el formulario, intenta agregar otra vez al usuario",
            )
    else:
        form = CuentaForms()
    return render(
        request,
        "admin/usuario/lista_usuario.html",
        {"usuario": queryset, "form": form},
    )



@login_required(login_url="inicio_sesion")
@protect_route
def perfil_admin(request):
    usuario_actual=request.user    
    if request.method == "POST":
        formulario = PerfilForms(request.POST)
        if formulario.is_valid():
            nombre = formulario.cleaned_data["nombre"]
            apellido = formulario.cleaned_data["apellido"]            
            telefono = formulario.cleaned_data["telefono"]
            password = formulario.cleaned_data["password"]                                                                        
        
            cuenta = Cuenta.objects.get(pk=usuario_actual.pk)        
            cuenta.nombre=nombre
            cuenta.apellido=apellido                                
            cuenta.telefono=telefono
            cuenta.password=password
            # Se verifica si se ingreso una nueva contraseña
            if password:
                cuenta.set_password(password)
            cuenta.save()
            messages.success(request, 'Perfil actualizado correctamente, Inicia sesión nuevamente')
            return redirect("inicio_sesion")
        else:                                                                              
            messages.error(request, 'Ha ocurrido un error al actualizar tu perfil, revisa el formulario otra vez')        
    else:
        datos_usuario = {
            "nombre": usuario_actual.nombre,
            "apellido": usuario_actual.apellido,            
            "telefono": usuario_actual.telefono,
        }
        formulario = PerfilForms(initial=datos_usuario)
        
    return render(request, "admin/usuario/perfil.html", {"form": formulario,  "usuario":usuario_actual})


'''

@login_required(login_url="inicio_sesion")
@protect_route
def detalle_usuario_admin(request, id_usuario):
    if request.method == "GET":
        detalle_usuario = get_object_or_404(Cuenta, pk=id_usuario)
        form = CuentaForms(instance=detalle_usuario)
        return render(
            request,
            "admin/usuario/detalle_usuario.html",
            {"detalle": detalle_usuario, "form": form},
        )
    else:
        try:
            # Actualizar
            detalle_usuario = get_object_or_404(Cuenta, pk=id_usuario)
            form = CuentaForms(request.POST, instance=detalle_usuario)
            form.save()
            messages.success(request, "Usuario actualizada")
            return redirect("lista_usuario")
        except:
            messages.error(
                request,
                "Ha ocurrido un error en el formulario, intenta actualizar otra vez el usuario",
            )
            return render(
                request,
                "admin/usuario/detalle_usuario.html",
                {"detalle": detalle_usuario, "form": form},
            )



@login_required(login_url="inicio_sesion")
@protect_route
def eliminar_usuario(request, id_usuario):
    Usuario = get_object_or_404(Cuenta, id=id_usuario)
    if request.method == "POST":
        Usuario.delete()
        messages.success(request, "Usuario eliminado")
        return redirect("lista_usuario")
    else:
        messages.error(request, "Ha ocurrido un error al eliminar un usuario")
'''
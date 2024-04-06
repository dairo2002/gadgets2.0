from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RegistroForms, CuentaForms
from config.decorators import protect_route
from django.contrib import auth, messages
from .models import Cuenta

# importaciones email
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from datetime import datetime, timedelta
from carrito.models import Carrito
from django.utils import timezone

# API
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import CuentaSerializer
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
                    "expiracion": timezone.now() + timedelta(minutes=5),
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
    if request.user.is_authenticated:
        return redirect("index")

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
                    return redirect("panel_admin")
                elif usuarios.is_staff:
                    auth.login(request, usuarios)
                    messages.success(
                        request, f"Bienvenido {usuarios.nombre} {usuarios.apellido}"
                    )

                    try:
                        cart = Carrito.objects.get(
                            session_id=request.session["nonuser"], completed=False
                        )

                        if Carrito.objects.filter(
                            usuario=request.user, completed=False
                        ).exists():
                            cart.usuario = None
                            cart.save()

                        else:
                            cart.usuario = request.user
                            cart.save()

                    except Exception as e:
                        print("Error ", e)
                    return redirect("index")
            else:
                messages.error(request, "Tu cuenta está desactivada.")
        else:
            messages.error(request, "Credenciales incorrectas")
            return redirect("inicio_sesion")
    return render(request, "client/cuenta/inicio_sesion.html")


@login_required(login_url="inicio_sesion")
def perfil(request):
    usuario_actual = request.user
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
            
            if Cuenta.objects.filter(correo_electronico=correo_electronico).exists():
                raise ValidationError('Este correo electrónico ya existe.')

            if Cuenta.objects.filter(username=usuario).exists():
                messages.error(request, "El nombre de usuario ya existe")
                return redirect("registrarse")

            # metodo create_user creado en ManejadorCuenta
            crear_usuario = Cuenta.objects.create_user(
                nombre=nombre,
                apellido=apellido,
                correo_electronico=correo_electronico,
                username=usuario,
                password=password,
            )
            
            crear_usuario.telefono = telefono
            crear_usuario.save()   
            return redirect("index")    
    else:
        '''obtener_usuario = Cuenta.objects.create_user(
            nombre=usuario_actual.nombre,
            apellido=usuario_actual.apellido,
            correo_electronico=usuario_actual.correo_electronico,            
            telefono=usuario_actual.telefono,
        )
        formulario = RegistroForms(initial=obtener_usuario)'''
        datos_usuario = {
            "nombre": usuario_actual.nombre,
            "apellido": usuario_actual.apellido,
            "correo_electronico": usuario_actual.correo_electronico,
            "telefono": usuario_actual.telefono,
        }
        formulario = RegistroForms(initial=datos_usuario)
        
    return render(request, "client/cuenta/perfil_usuario.html", {"form": formulario})


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
                "expiracion": timezone.now() + timedelta(minutes=5),
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
                    "actualizar ": str(token),
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


# @api_view(["POST"])
# # @permission_classes([IsAuthenticated])
# def logout(request):
#     try:
#         # token = request.GET.get("token") = Query parameter
#         #  token = request.data.get("token") = JSON
#         token = request.data.get("token")
#         token_obj = Token.objects.filter(key=token).first()
#         if token_obj:
#             # token.user.auth_token.delete()
#             token = token_obj.user
#             token_obj.delete()
#             return Response(
#                 {"success": True, "message": "Has cerrado sesión exitosamente."},
#                 status=status.HTTP_200_OK,
#             )
#         return Response(
#             {
#                 "error": False,
#                 "message": "No se ha encontrado un usuario con este token",
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#     except:
#         return Response(
#             {"error": False, "message": "No se ha encontrado el token en la petición"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )


@api_view(["POST"])
def logout(request):
    # Cierra la sesión del usuario
    auth.logout(request)
    return Response({"success": True, "message": "Sesión cerrada exitosamente."})


# ? corregir desactivar cuenta
@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def deactivate_account(request):
    try:
        token = request.data.get("token")
        token_obj = RefreshToken(key=token).first()

        if token_obj:
            user = token_obj.user
            user.is_active = False
            user.is_staff = False
            user.is_admin = False
            user.save()

            # Eliminar el token de autenticación
            token_obj.delete()

            # auth.logout(request)
            return Response(
                {"message": "Tu cuenta ha sido desactivada"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "No se ha encontrado un usuario con este token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except:
        return Response(
            {"message": "Ha ocurrido un error al desactivar la cuenta"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def deactivate_accountV2(request):
    # cuenta = Cuenta.objects.get(correo_electronico=request.user)
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

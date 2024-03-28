from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistroForms
from .models import Cuenta
from django.contrib import auth, messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

# importaciones email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils import timezone
from datetime import datetime, timedelta

from carrito.models import Carrito

# API
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes

from .serializers import CuentaSerializer

from django.http import HttpResponse
import pdb
import requests


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
        return redirect('index')

    # Verifica si la solicitud al servidor es de tipo POST
    if request.method == "POST":
        # Obtener los datos del formulario
        correo_electronico = request.POST["correo_electronico"]
        password = request.POST["password"]

        #  authenticate: Toma el correo electrónico y la contraseña ingresada, busca un usuario que coincida en la base de datos
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
                        cart = Carrito.objects.get(session_id=request.session['nonuser'], completed=False)
                        print("inicio sesion ",cart)
                        if Carrito.objects.filter(usuario=request.user, completed=False).exists():
                            cart.usuario=None                            
                            cart.save()
                            print("inicio sesion filtro ",cart)
                            # pdb.set_trace()
                        else:
                            cart.usuario = request.user
                            cart.save()
                            print("inicio sesion NO filtro ",cart)       

                    except Exception as e:
                        print("Error ",e)
                    return redirect("index")
            else:
                messages.error(request, "Tu cuenta está desactivada.")
        else:
            messages.error(request, "Credenciales incorrectas")
            return redirect("inicio_sesion")
    return render(request, "client/cuenta/inicio_sesion.html")

    # Verificar si hay un producto en el carrito existente y asociarlo al usuario
    """if usuarios is not None:
        try:
            # Obtener la sesion del carrito
            carrito_sesion = CarritoSesion.objects.get(
                carrito_session=_carrito_sesion(request)
            )
            carrito_existe = Carrito.objects.filter(
                carritoSesion=carrito_sesion
            ).exists()
            if carrito_existe:
                carrito = Carrito.objects.filter(carritoSesion=carrito_sesion)
                for articulo in carrito:
                    articulo.usuario = usuarios
                    articulo.save()
        except Exception as e:
            print(f"Error: ", {e})
        # Establece la sesion al usuario
        auth.login(request, usuarios)
        messages.success(
        request, f"Bienvenido {usuarios.nombre} {usuarios.apellido}"
        )
        # Creamos la ruta para que nos redirija a pedidos en caso tal que quiera hacer un pedido
        url = request.META.get("HTTP_REFERER")
        try:
            consulta = requests.utils.urlparse(url).query
            print("Consulta", consulta)
            params = dict(x.split("=") for x in consulta.split("&"))
            print("Parametro: ", params)
            if "next" in params:
                nextPage = params["next"]
                return redirect(nextPage)
        except:                    
            return redirect("index")
    else:
        messages.error(request, "Las credenciales son incorrectas")
        return redirect("inicio_sesion")
        return render(request, "client/cuenta/inicio_sesion.html")"""


@login_required(login_url="inicio_sesion")
def cerrar_sesion(request):
    auth.logout(request)
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect("inicio_sesion")



# @login_required(login_url="inicio_sesion")
# def cerrar_sesion(request):
#     auth.logout(request)
#     messages.success(request, "Has cerrado sesión exitosamente.")
#     return redirect("inicio_sesion")


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


# Validar que en api que las dos contraseñas concidan, sino hacer la validacion en movil
@api_view(["POST"])
def signupAPIView(request):
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
        # Genera un token para el usuario registrado

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
        # ruta de gmail que lo redirije a iniciar sesion
        # return redirect(
        #     "/cuenta/inicio_sesion/?command=verificacion&email=" + correo_electronico
        # )
        return Response(
            {
                "success": True,
                "message": "Por favor activa la cuenta ingresando al enlace enviado al correo electrónico",
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def loginAPIView(request):
    if request.method == "POST":
        correo_electronico = request.data.get("correo_electronico")
        password = request.data.get("password")

        usuario = auth.authenticate(
            correo_electronico=correo_electronico, password=password
        )

        if usuario is not None:
            token, created = Token.objects.get_or_create(user=usuario)
            if created:
                return Response(
                    {
                        "token": token.key,
                        "success": True,
                        "message": f"Bienvenido {usuario.nombre} {usuario.apellido}",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # Elmina las sesiones cuando ingresa un navegador, Le creamo un nuevo token cuando el usuario vaya a iniciar sesion
                token.delete()
                token = Token.objects.create(user=usuario)
                return Response(
                    {
                        "token": token.key,
                        "success": True,
                        "message": f"Bienvenido {usuario.nombre} {usuario.apellido}",
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"error": False, "message": "Las credenciales son incorrectas"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def logoutAPIView(request):
    try:
        token = request.GET.get("token")
        print(token)
        token = Token.objects.filter(key=token).first()

        if token:
            # user= token.user
            token.user.auth_token.delete()
            return Response(
                {"success": True, "message": "Has cerrado sesión exitosamente."}
            )

        return Response(
            {"error": False, "message": "No se ha encontrado un usuario con este token"}
        )
    except:
        return Response(
            {"error": False, "message": "No se ha encontrado el token en la petición"}
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
                {"error": "La cuenta no existe!"}, status=status.HTTP_404_NOT_FOUND
            )

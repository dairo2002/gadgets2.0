from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Carrito

@receiver(user_logged_in)
def asignar_carrito_al_usuario(sender, user, request, **kwargs):
    cart = Carrito.objects.get_or_create(usuario=user)[0]

from django.db import models
from django.urls import reverse
from django.utils import timezone
from cuenta.models import Cuenta
from django.db.models import Count, Avg
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.core.validators import FileExtensionValidator



class Categoria(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=30, unique=True)
    descuento = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    """
        - reverse: Función de Django para obtener URLs de vistas.
        - categoria_a_producto: Nombre de la vista.
        - args: Lista de argumentos para la vista.
        - self.slug: Atributo del objeto actual (una categoría).
    """

    def get_url_categoria(self):
        return reverse("categoria_a_producto", args=[self.slug])

    def __str__(self):
        return self.nombre
    
@receiver(pre_save, sender=Categoria)
def _post_save_receiver(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.nombre)


class Producto(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    descripcion = models.TextField(max_length=1000)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField()
    # FileExtensionValidator permite cargar imagenes con la extencion especifica que pasamos
    imagen = models.ImageField(
        upload_to="productos/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png"])],
    )
    disponible = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    def get_url_producto(self):
        return reverse("detalle_producto", args=[self.categoria.slug, self.slug])

    def precioFormatiado(self):
        return "{:,.0f}".format(self.precio).replace(',', '.')

    def descuentoFormatiado(self):
        return "{:,.0f}".format(self.aplicar_descuento()).replace(",", ".")
    
    def porcentajeDescFormtiado(self):
        return "{:.0f}".format(self.categoria.descuento)

    def aplicar_descuento(self):
        if (
            self.categoria.descuento
            and self.categoria.fecha_inicio
            and self.categoria.fecha_fin
        ):
            fecha_actual = timezone.now()
            if self.categoria.fecha_inicio <= fecha_actual <= self.categoria.fecha_fin:
                descuento_decimal = 1 - self.categoria.descuento / 100
                descuento = self.precio * descuento_decimal
                return descuento
            else:
                # Si la fecha actual está fuera del rango de fechas de descuento, limpiar los campos relacionados con el descuento
                self.categoria.descuento = None
                self.categoria.fecha_inicio = None
                self.categoria.fecha_fin = None
                self.categoria.save()
                return self.precio
        return self.precio        

    def promedioCalificacion(self):
        revisar = Valoraciones.objects.filter(producto=self, estado=True).aggregate(
            promedio=Avg("calificacion")
        )
        avg = 0
        if revisar["promedio"] is not None:
            avg = float(revisar["promedio"])
        return avg

    def contarCalificaciones(self):
        revisar = Valoraciones.objects.filter(producto=self, estado=True).aggregate(
            contar=Count("id")
        )
        contar = 0
        if revisar["contar"] is not None:
            contar = int(revisar["contar"])
        return contar


# se ejecuta antes de que el objecto llege a la DB
@receiver(pre_save, sender=Producto)
def _post_save_receiver(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.nombre)



class Valoraciones(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=500)
    calificacion = models.FloatField()
    estado = models.BooleanField(default=True)
    creado = models.DateField(default=timezone.now)
    actualizado = models.DateField(default=timezone.now)

    def __str__(self):
        return self.usuario.username

    # TODO Explicacion

    # ? Metodos get_url_categoria y get_url_producto
    # categoria_a_producto es el nombre de la URL, de la categoria
    # con el slug pasamos el id, pero es mostrado en texto
    # def get_url_categoria(self):
    # path("categoria/<slug:categoria_slug>", views.lista_categoria, name="categoria_a_producto"),
    # return reverse('categoria_a_producto', args=[self.slug])

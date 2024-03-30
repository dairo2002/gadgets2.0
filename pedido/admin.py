from django.contrib import admin
from .models import Pago, Pedido, Ventas
from django.utils.html import format_html
from django.contrib.contenttypes.admin import GenericTabularInline


class PagoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "metodo_pago",
        "cantidad_pagada",
        "cargar_imagen",
        "estado_pago",
        "estado_envio",
        "fecha",
    )

    # radio_fields = {'estado_pago': admin.VERTICAL}

    list_editable = ("estado_pago", "estado_envio")
    list_display_links = ["cargar_imagen", "usuario"]
    list_per_page = 5
    fieldsets = (
        (
            "Información del Pago",
            {
                "fields": ("usuario", "metodo_pago", "cantidad_pagada", "fecha"),
            },
        ),
        (
            "Estado del Pago y Envío",
            {
                "fields": ("estado_pago", "estado_envio"),
            },
        ),
        (
            "Cargar Imagen",
            {
                "fields": ("comprobante",),
            },
        ),
    )

    # Funcion creada para cargar la imagen del comprobante en el admin
    def cargar_imagen(self, obj):
        if obj.comprobante:
            return format_html(
                '<a href="{0}"><img src="{0}" style="max-height: 50px; max-width: 50px;"></a>'.format(
                    obj.comprobante.url
                )
            )

    cargar_imagen.short_description = "Comprobante"


class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "productos_list",
        "pago",
        "numero_pedido",
        "correo_electronico",
        "nombre",
        "apellido",
        "telefono",
        "direccion",
        "direccion_local",
        # Se llama la funcion para la conversion a mayúsculas
        "cod_postal_upper",
        "departamento",
        # "ciudad",
        "ordenado",
        "total_pedido",
    )

    def productos_list(self, obj):
        return ", ".join([producto.nombre for producto in obj.productos.all()])

    def cod_postal_upper(self, obj):
        return obj.codigo_postal.upper()

    # Cambiar el nombre para ser mostradro en el admin
    cod_postal_upper.short_description = "Código_postal"


class VentasAdmin(admin.ModelAdmin):
    list_display = (
        "pedido",
        "pago",
        "usuario",
        "producto",
        "cantidad",
        "precio",
        "ordenado",
        "fecha",
    )


admin.site.register(Pago, PagoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(Ventas, VentasAdmin)
from django.contrib import admin
from .models import Categoria, Producto, Valoraciones


class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nombre",)}
    list_display = ("nombre", "slug", "descuento", "fecha_inicio", "fecha_fin")





class ProductoAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nombre",)}
    list_display = ("nombre", "slug", "precio", "stock", "disponible", "categoria")



class ValoracionAdmin(admin.ModelAdmin):
    list_display = (
        "producto",
        "usuario",
        "comentario",
        "calificacion",
        "estado",
        "creado",
        "actualizado",
    )


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Valoraciones, ValoracionAdmin)

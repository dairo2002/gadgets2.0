from django.contrib import admin
from .models import Categoria, Producto


class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nombre",)}
    list_display = ("nombre", "slug", "descuento", "fecha_inicio", "fecha_fin")





class ProductoAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nombre",)}
    list_display = ("nombre", "slug", "precio", "stock", "disponible", "categoria")





admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)

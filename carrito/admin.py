from django.contrib import admin
from .models import Carrito, ItemCarrito

# class CarritoAdmin(admin.ModelAdmin):
#     list_display = (
#         "usuario",
#         "producto",
#         "cantidad",
#     )


admin.site.register(Carrito)
admin.site.register(ItemCarrito)

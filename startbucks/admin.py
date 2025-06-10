from django.contrib import admin
from .models import Producto, Carrito, ItemCarrito

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'cantidad')
    search_fields = ('nombre',)

class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'creado')
    search_fields = ('usuario__username',)

class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'producto', 'cantidad')
    search_fields = ('carrito__usuario__username', 'producto__nombre')

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(ItemCarrito, ItemCarritoAdmin)
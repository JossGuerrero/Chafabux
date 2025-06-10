from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/modificar/<int:item_id>/', views.modificar_cantidad, name='modificar_cantidad'),
    path('pagar/', views.pagar_paypal, name='pagar'),
    path('pago/exito/', views.pago_exito, name='pago_exito'),
    path('pago/cancelado/', views.pago_cancelado, name='pago_cancelado'),
    path('historial/', views.historial_compras, name='historial'),
    path('factura/<int:compra_id>/pdf/', views.factura_pdf, name='factura_pdf'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/foto/', views.editar_foto_perfil, name='editar_foto_perfil'),
    path('agregar-producto/', views.agregar_producto, name='agregar_producto'),
    path('producto/<int:producto_id>/', views.producto_detalle, name='producto_detalle'),
    path('cuentas/register/', views.register, name='register'),  # <-- Agrega esta línea
]
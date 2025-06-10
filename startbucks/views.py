from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
import paypalrestsdk
from django.conf import settings
from django.template.loader import get_template
from .models import Producto, Carrito, ItemCarrito, Compra, ItemCompra, Valoracion, Perfil
from .forms import PerfilUsuarioForm, ProductoForm, PerfilFotoForm
from xhtml2pdf import pisa

# ========== PERFIL Y USUARIO ==========

@login_required
def editar_foto_perfil(request):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PerfilFotoForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil_usuario')
    else:
        form = PerfilFotoForm(instance=perfil)
    return render(request, 'editar_foto_perfil.html', {'form': form, 'perfil': perfil})

@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil_usuario')
    else:
        form = PerfilUsuarioForm(instance=request.user)
    return render(request, 'perfil_usuario.html', {'form': form})

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        Perfil.objects.get_or_create(user=user)
        return redirect('login')
    return render(request, 'register.html', {'form': form})

# ========== PRODUCTOS ==========

@login_required
def agregar_producto(request):
    if not request.user.is_superuser:
        return HttpResponse("No tienes permisos para acceder aquí.")
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio')
    else:
        form = ProductoForm()
    return render(request, 'agregar_producto.html', {'form': form})

def inicio(request):
    productos = Producto.objects.all()
    nombre = request.GET.get('nombre', '').strip()
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')

    if nombre:
        productos = productos.filter(nombre__icontains=nombre)
    if precio_min != '':
        try:
            productos = productos.filter(precio__gte=float(precio_min))
        except ValueError:
            pass
    if precio_max != '':
        try:
            productos = productos.filter(precio__lte=float(precio_max))
        except ValueError:
            pass

    return render(request, 'inicio.html', {
        'productos': productos,
        'nombre': nombre,
        'precio_min': precio_min,
        'precio_max': precio_max
    })

@login_required
def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    valoraciones = producto.valoraciones.all().order_by('-fecha')
    if request.method == 'POST':
        calificacion = int(request.POST.get('calificacion'))
        comentario = request.POST.get('comentario', '')
        Valoracion.objects.create(
            producto=producto,
            usuario=request.user,
            calificacion=calificacion,
            comentario=comentario
        )
        return redirect('producto_detalle', producto_id=producto.id)
    return render(request, 'producto_detalle.html', {
        'producto': producto,
        'valoraciones': valoraciones
    })

# ========== CARRITO ==========

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto
    )
    if not creado:
        if item.cantidad < producto.cantidad:
            item.cantidad += 1
            item.save()
    else:
        if producto.cantidad > 0:
            item.cantidad = 1
            item.save()
    return redirect('inicio')

@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)
    for item in items:
        if item.cantidad > item.producto.cantidad:
            item.cantidad = item.producto.cantidad
            item.save()
    total = sum(item.producto.precio * item.cantidad for item in items)
    return render(request, 'carrito.html', {'items': items, 'total': total})

@login_required
def modificar_cantidad(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    producto = item.producto
    accion = request.POST.get('accion')

    if accion == 'mas':
        if item.cantidad < producto.cantidad:
            item.cantidad += 1
            item.save()
    elif accion == 'menos':
        if item.cantidad > 0:
            item.cantidad -= 1
            if item.cantidad == 0:
                item.delete()
            else:
                item.save()
    elif accion == 'eliminar':
        item.delete()
    return redirect('ver_carrito')

# ========== PAYPAL ==========

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

@login_required
def pagar_paypal(request):
    carrito = Carrito.objects.get(usuario=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)
    for item in items:
        if item.cantidad > item.producto.cantidad:
            item.cantidad = item.producto.cantidad
            item.save()
    total = sum(item.producto.precio * item.cantidad for item in items)
    if total == 0:
        return HttpResponse("No puedes pagar un carrito vacío.")

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": request.build_absolute_uri('/pago/exito/'),
            "cancel_url": request.build_absolute_uri('/pago/cancelado/')
        },
        "transactions": [{
            "item_list": {
                "items": [
                    {
                        "name": item.producto.nombre,
                        "sku": str(item.producto.id),
                        "price": str(item.producto.precio),
                        "currency": "USD",
                        "quantity": item.cantidad
                    } for item in items
                ]
            },
            "amount": {
                "total": str(total),
                "currency": "USD"
            },
            "description": "Compra en ChafaBux Café"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
        return HttpResponse("No se encontró la URL de aprobación de PayPal.")
    else:
        return HttpResponse("Error al crear el pago con PayPal.")

@login_required
def pago_exito(request):
    carrito = Carrito.objects.get(usuario=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)
    compra = Compra.objects.create(usuario=request.user)
    for item in items:
        producto = item.producto
        ItemCompra.objects.create(
            compra=compra,
            producto=producto,
            cantidad=item.cantidad,
            precio_unitario=producto.precio
        )
        producto.cantidad -= item.cantidad
        producto.save()
        item.delete()
    carrito.delete()
    return redirect('historial')

@login_required
def pago_cancelado(request):
    return render(request, 'pago_cancelado.html')

# ========== HISTORIAL Y FACTURA ==========

@login_required
def historial_compras(request):
    compras = Compra.objects.filter(usuario=request.user).order_by('-fecha')
    compras_con_total = []
    for compra in compras:
        items = []
        total = 0
        for item in compra.itemcompra_set.all():
            subtotal = item.cantidad * item.precio_unitario
            items.append({
                'nombre': item.producto.nombre,
                'cantidad': item.cantidad,
                'precio_unitario': item.precio_unitario,
                'subtotal': subtotal,
            })
            total += subtotal
        compras_con_total.append({'compra': compra, 'items': items, 'total': total})
    return render(request, 'historial.html', {'compras_con_total': compras_con_total})

@login_required
def factura_pdf(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id, usuario=request.user)
    items = []
    total = 0
    for item in compra.itemcompra_set.all():
        subtotal = item.cantidad * item.precio_unitario
        items.append({
            'nombre': item.producto.nombre,
            'cantidad': item.cantidad,
            'precio_unitario': item.precio_unitario,
            'subtotal': subtotal,
        })
        total += subtotal
    template = get_template('factura_pdf.html')
    html = template.render({'compra': compra, 'items': items, 'total': total})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{compra.id}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF')
    return response
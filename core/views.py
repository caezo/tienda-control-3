from datetime import date
from .zpoblar import poblar_bd
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.utils.safestring import SafeString
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Producto, Boleta, Carrito, DetalleBoleta, Bodega, Perfil
from .forms import ProductoForm, BodegaForm, IngresarForm, UsuarioForm, PerfilForm
from .forms import RegistroUsuarioForm, RegistroPerfilForm
from .templatetags.custom_filters import formatear_dinero, formatear_numero
from .tools import eliminar_registro, verificar_eliminar_registro, show_form_errors
from django.core.mail import send_mail
from .forms import UsuarioForm, PerfilForm  # Asegúrate de importar tus formularios
from django.db import transaction, IntegrityError
from django import template
from django.db import models






register = template.Library()

# *********************************************************************************************************#
#                                                                                                          #
# INSTRUCCIONES PARA EL ALUMNO, PUEDES SEGUIR EL VIDEO TUTORIAL, COMPLETAR EL CODIGO E INCORPORAR EL TUYO: #
#                                                                                                          #
# https://drive.google.com/drive/folders/1ObwMnpKmCXVbq3SMwJKlSRE0PCn0buk8?usp=drive_link                  #
#                                                                                                          #
# *********************************************************************************************************#

# Se usará el decorador "@user_passes_test" para realizar la autorización básica a las páginas.
# De este modo sólo entrarán a las páginas las personas que sean del tipo_usuario permitido.
# Si un usuario no autorizado intenta entrar a la página, será redirigido al inicio o a ingreso

# Revisar si el usuario es personal de la empresa (staff administrador o superusuario) autenticado y con cuenta activa
def es_personal_autenticado_y_activo(user):
    return (user.is_staff or user.is_superuser) and user.is_authenticated and user.is_active

# Revisar si el usuario no está autenticado, es decir, si aún está navegando como usuario anónimo
def es_usuario_anonimo(user):
    return user.is_anonymous

# Revisar si el usuario es un cliente (no es personal de la empresa) autenticado y con cuenta activa
def es_cliente_autenticado_y_activo(user):
    return (not user.is_staff and not user.is_superuser) and user.is_authenticated and user.is_active

def inicio(request):

    if request.method == 'POST':
        # Si la vista fue invocada con un POST es porque el usuario presionó el botón "Buscar" en la página principal.
        # Por lo anterior, se va a recuperar palabra clave del formulario que es el campo "buscar" (id="buscar"), 
        # que se encuentra en la página Base.html. El formulario de búsqueda se encuentra bajo el comentario 
        # "FORMULARIO DE BUSQUEDA" en la página Base.html.
        buscar = request.POST.get('buscar')

        # Se filtrarán todos los productos que contengan la palabra clave en el campo nombre
        registros = Producto.objects.filter(nombre__icontains=buscar).order_by('nombre')
    
    if request.method == 'GET':
        # Si la vista fue invocada con un GET, se devolverán todos los productos a la PAGINA
        registros = Producto.objects.all().order_by('nombre')

    # Como los productos tienen varios cálculos de descuentos por ofertas y subscripción, estos se realizarán
    # en una función a parte llamada "obtener_info_producto", mediante la cuál se devolverán las filas de los
    # productos, pero con campos nuevos donde los cálculos ya han sido realizados.
    productos = []
    for registro in registros:
        productos.append(obtener_info_producto(registro.id))

    context = { 'productos': productos }
    
    return render(request, 'core/inicio.html', context)

def ficha(request, producto_id):
    context = obtener_info_producto(producto_id)
    return render(request, 'core/ficha.html', context)

def nosotros(request):
    # CREAR: renderización de página
    return render(request, 'core/nosotros.html')

def premio(request):
    return render(request, 'core/premio.html')

@user_passes_test(es_usuario_anonimo, login_url='inicio')
def ingresar(request):

    if request.method == "POST":
        form = IngresarForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'¡Bienvenido(a) {user.first_name} {user.last_name}!')
                    return redirect(inicio)
                else:
                    messages.error(request, 'La cuenta está desactivada.')
            else:
                messages.error(request, 'La cuenta o la password no son correctos')
        else:
            messages.error(request, 'No se pudo ingresar al sistema')
            show_form_errors(request, [form])

    if request.method == "GET":

        form = IngresarForm()

    context = {
        'form':  IngresarForm(),
        'perfiles': Perfil.objects.all().order_by('tipo_usuario', 'subscrito'),
    }

    return render(request, "core/ingresar.html", context)

@login_required
def salir(request):
    nombre = request.user.first_name
    apellido = request.user.last_name
    messages.success(request, f'¡Hasta pronto {nombre} {apellido}!')
    logout(request)
    return redirect(inicio)

@user_passes_test(es_usuario_anonimo)
def registrarme(request):
    
    if request.method == 'POST':

        form_usuario = RegistroUsuarioForm(request.POST)
        form_perfil = RegistroPerfilForm(request.POST, request.FILES)

        if form_usuario.is_valid() and form_perfil.is_valid():
            usuario = form_usuario.save(commit=False)
            usuario.is_staff = False
            perfil = form_perfil.save(commit=False)
            usuario.save()
            perfil.usuario_id = usuario.id
            perfil.tipo_usuario = 'Cliente'
            perfil.save()
            premium = 'y aprovechar tus descuentos especiales como cliente PREMIUM' if hasattr(perfil, 'premium') and perfil.premium else ''
            mensaje = f'Tu cuenta de usuario: "{usuario.username}" ha sido creada con éxito. ¡Ya puedes iniciar sesión {premium}!'
            messages.success(request, mensaje)
            return redirect(ingresar)
        else:
            messages.error(request, 'No fue posible crear tu cuenta de cliente.')
        show_form_errors(request, [form_usuario, form_perfil])

    if request.method == 'GET':

        form_usuario = RegistroUsuarioForm()
        form_perfil = RegistroPerfilForm()

    context = {
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
    }

    return render(request, 'core/registrarme.html', context)


@login_required
def misdatos(request):
    usuario = request.user
    try:
        perfil = usuario.perfil
    except Perfil.DoesNotExist:
        perfil = None

    if request.method == 'POST':
        form_usuario = UsuarioForm(request.POST, instance=usuario)
        form_perfil = RegistroPerfilForm(request.POST, request.FILES, instance=perfil)

        if form_usuario.is_valid() and form_perfil.is_valid():
            usuario = form_usuario.save()
            perfil = form_perfil.save(commit=False)
            perfil.usuario = usuario
            perfil.save()
            messages.success(request, 'Tus datos han sido actualizados correctamente.')
            return redirect('misdatos')
        else:
            messages.error(request, 'No fue posible actualizar tus datos.')

    else:
        form_usuario = UsuarioForm(instance=usuario)
        form_perfil = RegistroPerfilForm(instance=perfil)

    context = {
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
    }

    return render(request, 'core/misdatos.html', context)
    usuario = request.user
    perfil = usuario.perfil if hasattr(usuario, 'perfil') else None

    if request.method == 'POST':
        form_usuario = UsuarioForm(request.POST, instance=usuario)
        form_perfil = RegistroPerfilForm(request.POST, request.FILES, instance=perfil)

        if form_usuario.is_valid() and form_perfil.is_valid():
            usuario = form_usuario.save()
            perfil = form_perfil.save(commit=False)
            perfil.usuario = usuario
            perfil.save()
            premium = 'y aprovechar tus descuentos especiales como cliente PREMIUM' if perfil.premium else ''
            mensaje = f'Tus datos han sido actualizados correctamente {premium}!'
            messages.success(request, mensaje)
            return redirect('misdatos')
        else:
            messages.error(request, 'No fue posible actualizar tus datos.')

    else:
        form_usuario = UsuarioForm(instance=usuario)
        form_perfil = RegistroPerfilForm(instance=perfil)

    context = {
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
    }

    return render(request, 'core/misdatos.html', context)

@login_required
def boleta(request, nro_boleta):
    # Obtener la boleta correspondiente al número de boleta
    boleta = get_object_or_404(Boleta, nro_boleta=nro_boleta)
    detalles_boleta = DetalleBoleta.objects.filter(boleta=boleta)
    # CREAR: Aquí podrías agregar lógica adicional si necesitas procesar más datos relacionados con la boleta

    # Preparar el contexto con la boleta
    context = {
        
        'boleta': boleta,
        'detalles_boleta': detalles_boleta
        # Aquí podrías incluir más datos relacionados con la boleta si los necesitas
    }

    # Renderizar la plantilla 'boleta.html' con el contexto creado
    return render(request, 'core/boleta.html', context)

@user_passes_test(es_personal_autenticado_y_activo)
def ventas(request):
    # Obtener todas las boletas ordenadas por fecha de venta (o como necesites)
    historial_boletas = Boleta.objects.all().order_by('-fecha_venta')

    # Variable de contexto para enviar historial de boletas
    context = {
        'historial': historial_boletas
    }

    return render(request, 'core/ventas.html', context)


@user_passes_test(es_personal_autenticado_y_activo)
def productos(request, accion, id):
    if request.method == 'POST':
        # Procesar formulario si se envió por POST
        if accion == 'crear':
            form = ProductoForm(request.POST, request.FILES)
        elif accion == 'actualizar':
            form = ProductoForm(request.POST, request.FILES, instance=get_object_or_404(Producto, id=id))
        
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'El producto "{producto}" se logró {accion} correctamente')
            return redirect('productos', 'actualizar', producto.id)
        else:
            messages.error(request, 'No fue posible guardar el producto')
            # En caso de error, manejar el form aquí si es necesario
    else:
        form = None  # Definir form inicialmente como None
        
        if accion == 'crear':
            form = ProductoForm()
        elif accion == 'actualizar':
            form = ProductoForm(instance=get_object_or_404(Producto, id=id))
        elif accion == 'eliminar':
            try:
                with transaction.atomic():
                    producto = get_object_or_404(Producto, id=id)
                
                    # Eliminar objetos relacionados primero (ejemplo: Bodega)
                    Bodega.objects.filter(producto=producto).delete()

                    # Ahora eliminar el producto
                    producto.delete()
            
                    messages.success(request, 'Producto eliminado correctamente.')
            
            except IntegrityError:
                messages.error(request, 'No se puede eliminar el producto.')

    productos = Producto.objects.all()
    return render(request, "core/productos.html", {'form': form, 'productos': productos})
@user_passes_test(es_personal_autenticado_y_activo)
def usuarios(request, accion, id):
    
    if request.method == 'POST':
        if accion == 'crear':
            form_usuario = UsuarioForm(request.POST)
            form_perfil = PerfilForm(request.POST, request.FILES)

            if form_usuario.is_valid() and form_perfil.is_valid():
                usuario = form_usuario.save(commit=False)
                usuario.is_staff = False  # Asignar el rol adecuado
                usuario.save()

                perfil = form_perfil.save(commit=False)
                perfil.usuario = usuario
                perfil.save()

                return redirect(reverse('usuarios', args=['crear', 0]))

        elif accion == 'actualizar':
            usuario = get_object_or_404(User, id=id)
            perfil = get_object_or_404(Perfil, usuario=usuario)

            form_usuario = UsuarioForm(request.POST, instance=usuario)
            form_perfil = PerfilForm(request.POST, request.FILES, instance=perfil)

            if form_usuario.is_valid() and form_perfil.is_valid():
                form_usuario.save()
                form_perfil.save()

                return redirect(reverse('usuarios', args=['actualizar', id]))

    elif request.method == 'GET':
        if accion == 'eliminar':
            try:
                with transaction.atomic():
                    usuario = get_object_or_404(User, id=id)
                    # Eliminar objetos relacionados primero
                    Perfil.objects.filter(usuario=usuario).delete()
                    # Ahora eliminar el usuario
                    usuario.delete()
                messages.success(request, 'Usuario eliminado correctamente.')
                return redirect(reverse('usuarios', args=['crear', 0]))
            except IntegrityError:
                messages.error(request, 'No se puede eliminar el usuario debido a restricciones de clave foránea.')
                return redirect(reverse('usuarios', args=['crear', 0]))


        elif accion == 'crear':
            form_usuario = UsuarioForm()
            form_perfil = PerfilForm()

        else:  # accion == 'actualizar'
            usuario = get_object_or_404(User, id=id)
            perfil = get_object_or_404(Perfil, usuario=usuario)
            form_usuario = UsuarioForm(instance=usuario)
            form_perfil = PerfilForm(instance=perfil)

    context = {
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
        'usuarios': User.objects.all(),  # Obtener todos los usuarios para mostrar en la tabla
    }

    return render(request, 'core/usuarios.html', context)  
@user_passes_test(es_personal_autenticado_y_activo)


@user_passes_test(es_personal_autenticado_y_activo)
def eliminar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    usuario.delete()
    messages.success(request, 'Usuario eliminado con éxito')
    return redirect('usuarios')
@user_passes_test(es_personal_autenticado_y_activo)
def bodega(request):

    if request.method == 'POST':
        producto_id=request.POST.get('producto')
        producto =Producto.objects.get(id=producto_id)
        cantidad=int(request.POST.get('cantidad'))
        for i in range(1,cantidad+1):
            Bodega.objects.create(producto=producto)
        
            if cantidad == 1:
                messages.success(request, f'Se ha agregado 1 nuevo "{producto.nombre}" a la bodega.')
            else:
                messages.success(request, f'Se han agregado {cantidad} nuevos "{producto.nombre}" a la bodega.')    
        pass

    registros = Bodega.objects.all()
    lista = []
    for registro in registros:
        vendido = DetalleBoleta.objects.filter(bodega=registro).exists()
        item = {
            'bodega_id': registro.id,
            'nombre_categoria': registro.producto.categoria.nombre,
            'nombre_producto': registro.producto.nombre,
            'estado': 'Vendido' if vendido else 'En bodega',
            'imagen': registro.producto.imagen,
        }
        lista.append(item)

    context = {
        'form': BodegaForm(),
        'productos': lista,
    }
    
    return render(request, 'core/bodega.html', context)


@user_passes_test(es_personal_autenticado_y_activo)
def obtener_productos(request):
    # La vista obtener_productos la usa la pagina "Administracion de bodega", para
    # filtrar el combobox de productos cuando el usuario selecciona una categoria
    
    categoria_id=request.Get.get('categoria')
    producto=Producto.objects.filter(categoria_id=categoria_id)
    data=[
        {
            'id':producto.id,
            'nombre':producto.nombre,
            'imagen':producto.imagen.url
        } for producto in productos
    ]
    # CREAR: Un JSON para devolver los productos que corresponden a la categoria

    
    return JsonResponse(data, safe=False)

@user_passes_test(es_personal_autenticado_y_activo)
def eliminar_producto_en_bodega(request, id):
    producto = get_object_or_404(Bodega, id=id)
    if not DetalleBoleta.objects.filter(bodega=producto).exists():
        producto.delete()
        messages.success(request, 'El producto ha sido eliminado exitosamente.')
    else:
        messages.error(request, 'No se puede eliminar un producto vendido.')
    return redirect('bodega')

@user_passes_test(es_cliente_autenticado_y_activo)
def miscompras(request):
    # Obtener el perfil del cliente actual
    perfil_cliente = get_object_or_404(Perfil, usuario=request.user)
    
    # Obtener todas las boletas del cliente ordenadas por fecha de venta
    boletas_cliente = Boleta.objects.filter(cliente=perfil_cliente).order_by('-fecha_venta')

    # Preparar una lista de compras con detalles
    compras = []
    for boleta in boletas_cliente:
        detalles_boleta = DetalleBoleta.objects.filter(boleta=boleta)
        compra = {
            'boleta': boleta,
            'detalles_boleta': detalles_boleta
        }
        compras.append(compra)

    # Crear el contexto con el historial de compras del cliente
    context = {
        'historial': boletas_cliente,  # Usar 'historial' para que coincida con la plantilla
        'compras': compras  # Mantener 'compras' si deseas mostrar los detalles en algún otro lugar
    }

    return render(request, 'core/miscompras.html', context)


# ***********************************************************************
# FUNCIONES Y VISTAS AUXILIARES QUE SE ENTREGAN PROGRAMADAS AL ALUMNO
# ***********************************************************************

# VISTA PARA CAMBIAR ESTADO DE LA BOLETA

@user_passes_test(es_personal_autenticado_y_activo)
def cambiar_estado_boleta(request, nro_boleta, estado):
    boleta = Boleta.objects.get(nro_boleta=nro_boleta)
    if estado == 'Anulado':
        # Anular boleta, dejando la fecha de anulación como hoy y limpiando las otras fechas
        boleta.fecha_venta = date.today()
        boleta.fecha_despacho = None
        boleta.fecha_entrega = None
    elif estado == 'Vendido':
        # Devolver la boleta al estado recien vendida al dia de hoy, y sin despacho ni entrega
        boleta.fecha_venta = date.today()
        boleta.fecha_despacho = None
        boleta.fecha_entrega = None
    elif estado == 'Despachado':
        # Cambiar boleta a estado despachado, se conserva la fecha de venta y se limpia la fecha de entrega
        boleta.fecha_despacho = date.today()
        boleta.fecha_entrega = None
    elif estado == 'Entregado':
        # Cambiar boleta a estado entregado, pero hay que ver que estado actual tiene la boleta
        if boleta.estado == 'Vendido':
            # La boleta esta emitida, pero sin despacho ni entrega, entonces despachamos y entregamos hoy
            boleta.fecha_despacho = date.today()
            boleta.fecha_entrega = date.today()
        elif boleta.estado == 'Despachado':
            # La boleta esta despachada, entonces entregamos hoy
            boleta.fecha_entrega = date.today()
        elif boleta.estado == 'Entregado':
            # La boleta esta entregada, pero si se trata de un error entonces entregamos hoy
            boleta.fecha_entrega = date.today()
    boleta.estado = estado
    boleta.save()
    return redirect(ventas)

# FUNCIONES AUXILIARES PARA OBTENER: INFORMACION DE PRODUCTOS, CALCULOS DE PRECIOS Y OFERTAS

def obtener_info_producto(producto_id):

    # Obtener el producto con el id indicado en "producto_id"
    producto = Producto.objects.get(id=producto_id)

    # Se verificará cuántos productos hay en la bodega que tengan el id indicado en "producto_id".
    # Para lograrlo se filtrarán en primer lugar los productos con el id indicado. Luego, se 
    # realizará un JOIN con la tabla de "DetalleBoleta" que es donde se indican los productos
    # que se han vendido desde la bodega, sin olvidar que los modelos funcionan con Orientación
    # a Objetos, lo que hace que las consultas sean un poco diferentes a las de SQL. 
    # DetalleBoleta está relacionada con la tabla Bodega por medio de su propiedad "bodega",
    # la cual internamente agrega en la tabla DetalleBoleta el campo "bodega_id", que permite
    # que se relacione con la tabla Bodega. Para calcular cuántos productos quedan en la Bodega
    # se debe excluir aquellos que ya fueron vendidos, lo que se logra con la condición
    # "detalleboleta__isnull=False", es decir, se seleccionarán aquellos registros de Bodega
    # cuya relación con la tabla de DetalleBoleta esté en NULL, osea los que no han sido vendidos.
    # Si un producto de la Bodega estuviera vendido, entonces tendría su relación "detalleboleta"
    # con un valor diferente de NULL, ya que el campo "bodega_id" de la tabla DetalleBoleta
    # tendría el valor del id de Bodega del producto que se vendió.
    stock = Bodega.objects.filter(producto_id=producto_id).exclude(detalleboleta__isnull=False).count()
    
    # Preparar texto para mostrar estado: en oferta, sin oferta y agotado
    con_oferta = f'<span class="text-primary"> EN OFERTA {producto.descuento_oferta}% DE DESCUENTO </span>'
    sin_oferta = '<span class="text-success"> DISPONIBLE EN BODEGA </span>'
    agotado = '<span class="text-danger"> AGOTADO </span>'

    if stock == 0:
        estado = agotado
    else:
        estado = sin_oferta if producto.descuento_oferta == 0 else con_oferta

    # Preparar texto para indicar cantidad de productos en stock
    en_stock = f'En stock: {formatear_numero(stock)} {"unidad" if stock == 1 else "unidades"}'
   
    return {
        'id': producto.id,
        'nombre': producto.nombre,
        'descripcion': producto.descripcion,
        'imagen': producto.imagen,
        'html_estado': estado,
        'html_precio': obtener_html_precios_producto(producto),
        'html_stock': en_stock,
    }

def obtener_html_precios_producto(producto):
    
    precio_normal, precio_oferta, precio_subscr, hay_desc_oferta, hay_desc_subscr = calcular_precios_producto(producto)
    
    normal = f'Precio: {formatear_dinero(precio_normal)}'
    tachar = f'Precio: <span class="text-decoration-line-through"> {formatear_dinero(precio_normal)} </span>'
    oferta = f'Oferta: <span class="text-success"> {formatear_dinero(precio_oferta)} </span>'
    subscr = f'Subscrito: <span class="text-danger"> {formatear_dinero(precio_subscr)} </span>'

    if hay_desc_oferta > 0:
        texto_precio = f'{tachar}<br>{oferta}'
    else:
        texto_precio = normal

    if hay_desc_subscr > 0:
        texto_precio += f'<br>{subscr}'

    return texto_precio

def calcular_precios_producto(producto):
    precio_normal = producto.precio
    precio_oferta = producto.precio * (100 - producto.descuento_oferta) / 100
    precio_subscr = producto.precio * (100 - (producto.descuento_oferta + producto.descuento_subscriptor)) / 100
    hay_desc_oferta = producto.descuento_oferta > 0
    hay_desc_subscr = producto.descuento_subscriptor > 0
    return precio_normal, precio_oferta, precio_subscr, hay_desc_oferta, hay_desc_subscr

# VISTAS y FUNCIONES DE COMPRAS

def comprar_ahora(request):
    messages.error(request, f'El pago aún no ha sido implementado.')
    return redirect(inicio)

@user_passes_test(es_cliente_autenticado_y_activo)
def carrito(request):

    detalle_carrito = Carrito.objects.filter(cliente=request.user.perfil)

    total_a_pagar = 0
    for item in detalle_carrito:
        total_a_pagar += item.precio_a_pagar
    monto_sin_iva = int(round(total_a_pagar / 1.19))
    iva = total_a_pagar - monto_sin_iva

    context = {
        'detalle_carrito': detalle_carrito,
        'monto_sin_iva': monto_sin_iva,
        'iva': iva,
        'total_a_pagar': total_a_pagar,
    }

    return render(request, 'core/carrito.html', context)

def agregar_producto_al_carrito(request, producto_id):

    if es_personal_autenticado_y_activo(request.user):
        messages.error(request, f'Para poder comprar debes tener cuenta de Cliente, pero tu cuenta es de {request.user.perfil.tipo_usuario}.')
        return redirect(inicio)
    elif es_usuario_anonimo(request.user):
        messages.info(request, 'Para poder comprar, primero debes registrarte como cliente.')
        return redirect(registrarme)

    perfil = request.user.perfil
    producto = Producto.objects.get(id=producto_id)

    precio_normal, precio_oferta, precio_subscr, hay_desc_oferta, hay_desc_subscr = calcular_precios_producto(producto)

    precio = producto.precio
    descuento_subscriptor = producto.descuento_subscriptor if perfil.subscrito else 0
    descuento_total=producto.descuento_subscriptor + producto.descuento_oferta if perfil.subscrito else producto.descuento_oferta
    precio_a_pagar = precio_subscr if perfil.subscrito else precio_oferta
    descuentos = precio - precio_subscr if perfil.subscrito else precio - precio_oferta

    Carrito.objects.create(
        cliente=perfil,
        producto=producto,
        precio=precio,
        descuento_subscriptor=descuento_subscriptor,
        descuento_oferta=producto.descuento_oferta,
        descuento_total=descuento_total,
        descuentos=descuentos,
        precio_a_pagar=precio_a_pagar
    )

    return redirect(ficha, producto_id)

@user_passes_test(es_cliente_autenticado_y_activo)
def eliminar_producto_en_carrito(request, carrito_id):
    Carrito.objects.get(id=carrito_id).delete()
    return redirect(carrito)

@user_passes_test(es_cliente_autenticado_y_activo)
def vaciar_carrito(request):
    productos_carrito = Carrito.objects.filter(cliente=request.user.perfil)
    if productos_carrito.exists():
        productos_carrito.delete()
        messages.info(request, 'Se ha cancelado la compra, el carrito se encuentra vacío.')
    return redirect(carrito)

def eliminar_producto(request, id):
    if request.method == "POST":
        producto = get_object_or_404(Producto, id=id)
        producto.delete()
        return redirect("agregar_productos")
    return JsonResponse({"Error": "Método no permitido."}, status=405)

# CAMBIO DE PASSWORD Y ENVIO DE PASSWORD PROVISORIA POR CORREO

@login_required
def mipassword(request):

    if request.method == 'POST':

        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu contraseña ha sido actualizada con éxito, ingresa de nuevo con tu nueva contraseña.')
            return redirect(ingresar)
        else:
            messages.error(request, 'Tu contraseña no pudo ser actualizada.')
            show_form_errors(request, [form])
    
    if request.method == 'GET':

        form = PasswordChangeForm(user=request.user)

    context = {
        'form': form
    }

    return render(request, 'core/mipassword.html', context)

@user_passes_test(es_personal_autenticado_y_activo)
def cambiar_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        existe = User.objects.filter(username=username).exists()
        if existe:
            user = User.objects.get(username=username)
            if user is not None:
                if user.is_active:
                    password = User.objects.make_random_password()
                    user.set_password(password)
                    user.save()
                    enviado = enviar_correo_cambio_password(request, user, password)
                    if enviado:
                        messages.success(request, f'Una nueva contraseña fue enviada al usuario {user.first_name} {user.last_name}')
                    else:
                        messages.error(request, f'No fue posible enviar la contraseña al usuario {user.first_name} {user.last_name}, intente nuevamente más tarde')
                else:
                    messages.error(request, 'La cuenta está desactivada.')
            else:
                messages.error(request, 'La cuenta o la password no son correctos')
        else:
            messages.error(request, 'El usuario al que quiere generar una nueva contraseña ya no existe en el sistema')
    return redirect(usuarios, 'crear', '0')

def enviar_correo_cambio_password(request, user, password):
    try:
        # Revisar "CONFIGURACIÓN PARA ENVIAR CORREOS ELECTRÓNICOS A TRAVÉS DEL SERVIDOR DE GMAIL" en settings.py 
        subject = 'Cambio de contraseña Sword Games Shop'
        url_ingresar = request.build_absolute_uri(reverse(ingresar))
        message = render(request, 'common/formato_correo.html', {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_password': password,
            'link_to_login': url_ingresar,
        })
        from_email = 'info@faithfulpet.com'  # La dirección de correo que aparecerá como remitente
        recipient_list = []
        recipient_list.append(user.email)
        # Enviar el correo
        send_mail(subject=subject, message='', from_email=from_email, recipient_list=recipient_list
            , html_message=message.content.decode('utf-8'))
        return True
    except:
        return False

# POBLAR BASE DE DATOS CON REGISTROS DE PRUEBA

def poblar(request):
    # Permite poblar la base de datos con valores de prueba en todas sus tablas.
    # Opcionalmente se le puede enviar un correo único, para que los Administradores
    # del sistema puedan probar el cambio de password de los usuarios, en la página
    # de "Adminstración de usuarios".
    poblar_bd('cri.gomezv@profesor.duoc.cl')
    return redirect(inicio)
def administracion(request):
    
    return render(request, 'core/administracion.html', administracion)
def administrar(request):

    return render(request, 'core/administrar.html', administrar)
def registro(request):
    return render(request, 'registro.html')

def tu_vista(request):
    productos = Producto.objects.all()  # Obtener todos los productos
    form = TuFormulario()  # Instanciar el formulario que quieres usar

    # Renderizar la plantilla 'tu_template.html' con el formulario y los productos
    return render(request, 'tu_template.html', {'form': form, 'productos': productos})

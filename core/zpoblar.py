import sqlite3
from django.contrib.auth.models import User, Permission
from django.db import connection
from datetime import date, timedelta
from random import randint
from core.models import Categoria, Producto, Carrito, Perfil, Boleta, DetalleBoleta, Bodega

def eliminar_tabla(nombre_tabla):
    conexion = sqlite3.connect('db.sqlite3')
    cursor = conexion.cursor()
    cursor.execute(f"DELETE FROM {nombre_tabla}")
    conexion.commit()
    conexion.close()

def exec_sql(query):
    with connection.cursor() as cursor:
        cursor.execute(query)

def crear_usuario(username, tipo, nombre, apellido, correo, es_superusuario, 
    es_staff, rut, direccion, subscrito, imagen):

    try:
        print(f'Verificar si existe usuario {username}.')

        if User.objects.filter(username=username).exists():
            print(f'   Eliminar {username}')
            User.objects.get(username=username).delete()
            print(f'   Eliminado {username}')
        
        print(f'Iniciando creación de usuario {username}.')

        usuario = None
        if tipo == 'Superusuario':
            print('    Crear Superuser')
            usuario = User.objects.create_superuser(username=username, password='Duoc@123')
        else:
            print('    Crear User')
            usuario = User.objects.create_user(username=username, password='Duoc@123')

        if tipo == 'Administrador':
            print('    Es administrador')
            usuario.is_staff = es_staff
            
        usuario.first_name = nombre
        usuario.last_name = apellido
        usuario.email = correo
        usuario.save()

        if tipo == 'Administrador':
            print(f'    Dar permisos a core y apirest')
            permisos = Permission.objects.filter(content_type__app_label__in=['core', 'apirest'])
            usuario.user_permissions.set(permisos)
            usuario.save()
 
        print(f'    Crear perfil: RUT {rut}, Subscrito {subscrito}, Imagen {imagen}')
        Perfil.objects.create(
            usuario=usuario, 
            tipo_usuario=tipo,
            rut=rut,
            direccion=direccion,
            subscrito=subscrito,
            imagen=imagen)
        print("    Creado correctamente")
    except Exception as err:
        print(f"    Error: {err}")

def eliminar_tablas():
    eliminar_tabla('auth_user_groups')
    eliminar_tabla('auth_user_user_permissions')
    eliminar_tabla('auth_group_permissions')
    eliminar_tabla('auth_group')
    eliminar_tabla('auth_permission')
    eliminar_tabla('django_admin_log')
    eliminar_tabla('django_content_type')
    #eliminar_tabla('django_migrations')
    eliminar_tabla('django_session')
    eliminar_tabla('Bodega')
    eliminar_tabla('DetalleBoleta')
    eliminar_tabla('Boleta')
    eliminar_tabla('Perfil')
    eliminar_tabla('Carrito')
    eliminar_tabla('Producto')
    eliminar_tabla('Categoria')
    #eliminar_tabla('authtoken_token')
    eliminar_tabla('auth_user')

def poblar_bd(test_user_email=''):
    eliminar_tablas()

    crear_usuario(
        username='jgonzalez',
        tipo='Superusuario', 
        nombre='jesus', 
        apellido='gonzalez', 
        correo='jgonzalez@gmail.com', 
        es_superusuario=True, 
        es_staff=False, 
        rut='25342346-0',	
        direccion='vecinal 70, las condes, \nregion metropolitana \nchile', 
        subscrito=True, 
     
        imagen='perfiles/jesus_perfil.jfif')


    crear_usuario(
        username='cliberona',
        tipo='Cliente', 
        nombre='Constanza', 
        apellido='Liberona', 
        correo= 'con.perezl@duocuc.cl', 
        es_superusuario=False, 
        es_staff=False, 
        rut='20377842-2', 
        direccion='parcela 21, paine \nregion Metropolitana \nChile', 
        subscrito=True, 
        imagen='perfiles/fotomujer1.jpg')

    crear_usuario(
        username='gkatalinic',
        tipo='Cliente', 
        nombre='Georgui', 
        apellido='Katalinic', 
        correo='ge.katalinic@duocuc.cl', 
        es_superusuario=False, 
        es_staff=False, 
        rut='19659195-8', 
        direccion='Condell 450', 
        subscrito=False, 
        imagen='perfiles/georgui.jpg')


    crear_usuario(
        username='cr.ruizc',
        tipo='Administrador', 
        nombre='Cristian', 
        apellido='Ruiz', 
        correo= 'cr.ruizc@duocuc.cl', 
        es_superusuario=False, 
        es_staff=True, 
        rut='18784741-9', 
        direccion='Agustinas 1810, \nSantiago Centro \nSantiago', 
        subscrito=False, 
        imagen='perfiles/foto_hombre_1.jpg')

    
    categorias_data = [
        { 'id': 1, 'nombre': 'Acción'},
        { 'id': 2, 'nombre': 'Aventura'},
        { 'id': 3, 'nombre': 'Estrategia'},
        { 'id': 4, 'nombre': 'RPG'},
    ]

    print('Crear categorías')
    for categoria in categorias_data:
        Categoria.objects.create(**categoria)
    print('Categorías creadas correctamente')

    productos_data = [
        # Categoría "Acción" (8 juegos)
    {
        'id': 1,
        'categoria': Categoria.objects.get(id=1),
        'nombre': 'The Last of Us Part II',
        'descripcion': 'Embárcate en un emocionante viaje de supervivencia y venganza en un mundo devastado por una pandemia. En The Last of Us Part II, sigues la historia de Ellie mientras enfrenta nuevos peligros y desafíos morales en su búsqueda de justicia.',
        'precio': 49990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 15,
        'imagen': 'productos/the_last_of_us_2.jpeg'
    },
    {
        'id': 2,
        'categoria': Categoria.objects.get(id=1),
        'nombre': 'Battlefield: 2042',
        'descripcion': 'Battlefield: 2042 es un shooter de acción desarrollado por DICE y publicado por Electronic Arts. El juego se desarrolla en un futuro cercano, donde eventos climáticos extremos han desencadenado conflictos globales y alterado el paisaje de batalla de manera dinámica. Los jugadores podrán participar en intensas guerras a gran escala con hasta 128 jugadores en mapas enormes, utilizando una variedad de armas y vehículos militares para dominar el campo de batalla. ',
        'precio': 19990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 15,
        'imagen': 'productos/bettlefield_2042.jpeg'
    },
    {
        'id': 3,
        'categoria': Categoria.objects.get(id=1),
        'nombre': 'Ghost of Tsushima',
        'descripcion': 'Ghost of Tsushima es un juego de acción y aventura desarrollado por Sucker Punch Productions y publicado por Sony Interactive Entertainment. Ambientado en el Japón feudal, el juego sigue a Jin Sakai, un samurái en una misión para proteger su isla de Tsushima de la invasión mongol.',
        'precio': 39990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 15,
        'imagen': 'productos/ghost.jpeg'
    },
    {
        'id': 4,
        'categoria': Categoria.objects.get(id=1),
        'nombre': 'Deathloop',
        'descripcion': 'Deathloop es un juego de disparos en primera persona desarrollado por Arkane Studios y publicado por Bethesda Softworks. Ambientado en la isla ficticia de Blackreef, juegas como Colt, un asesino atrapado en un bucle temporal que debe eliminar ocho objetivos antes de que se reinicie el ciclo.',
        'precio': 19990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 10,
        'imagen': 'productos/death.jpeg'
    },
    {
        'id': 5,
        'categoria': Categoria.objects.get(id=1),
        'nombre': 'Marvel\'s Spider-Man',
        'descripcion': 'Sumérgete en la piel del icónico superhéroe en Marvel\'s Spider-Man para PlayStation 4. Disfruta de una aventura de acción épica mientras balanceas por la ciudad de Nueva York, luchas contra villanos legendarios y enfrentas desafíos tanto en la vida de Peter Parker como en la de Spider-Man. Domina el arte del parkour urbano y desbloquea nuevas habilidades mientras proteges la ciudad de amenazas cada vez más peligrosas.',
        'precio': 39990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 20,
        'imagen': 'productos/spiderman_ps4.jpeg'
    },
    {
        'id': 6,
        'categoria': Categoria.objects.get(id=1),
        'nombre': 'Destiny 2',
        'descripcion': 'Embárcate en una aventura épica en Destiny 2, un shooter de acción en primera persona desarrollado por Bungie. Explora planetas exóticos, completa misiones y desafíos, y lucha contra enemigos poderosos en un universo en constante expansión. Forma equipo con otros jugadores en emocionantes modos multijugador y coopera para derrotar a amenazas intergalácticas.',
        'precio': 29990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 0,
        'imagen': 'productos/destiny2.jpeg'
    },
    {
        'id': 7,
        'categoria': Categoria.objects.get(id=1),
        'nombre': 'Far Cry 6',
        'descripcion': 'Far Cry 6 es un juego de acción y aventuras en primera persona desarrollado por Ubisoft Toronto y publicado por Ubisoft. El juego se desarrolla en Yara, una isla ficticia inspirada en Cuba, gobernada por un dictador opresivo. Encarnas a Dani Rojas, un guerrillero que se une a la resistencia para liberar a su país del régimen brutal de Anton Castillo.',
        'precio': 69990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 0,
        'imagen': 'productos/farcry6.png'
    },
    {
        'id': 8,
        'categoria': Categoria.objects.get(id=1),
        'nombre': 'Ghost Recon: Phantoms',
        'descripcion': 'Embárcate en misiones secretas en Ghost Recon: Phantoms, donde controlarás a un equipo de fuerzas especiales en operaciones encubiertas contra enemigos globales. Utiliza tecnología avanzada y tácticas sigilosas para completar objetivos críticos.',
        'precio': 4990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 15,
        'imagen': 'productos/ghostrecon.jpg'
    },
    # Categoría "Aventura" (4 juegos)
    {
        'id': 9,
        'categoria': Categoria.objects.get(id=2),
        'nombre': 'Valkyrie Elysium',
        'descripcion': 'Prepárate para una aventura inolvidable en PS5 con Valkyrie Elysium. Explora un vasto mundo abierto lleno de secretos ocultos, criaturas mágicas y paisajes impresionantes. Utiliza tus habilidades para resolver acertijos antiguos y enfrentarte a enemigos poderosos mientras desentrañas la misteriosa historia de Elysium.',
        'precio': 5990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 0,
        'imagen': 'productos/Valkyrie_Elysium.png'
    },
    {
        'id': 10,
        'categoria': Categoria.objects.get(id=2),
        'nombre': 'Uncharted 3: Drake\'s Deception',
        'descripcion': 'Uncharted 3: Drake\'s Deception es un juego de acción y aventuras desarrollado por Naughty Dog y publicado por Sony Computer Entertainment. El juego sigue al cazador de tesoros Nathan Drake en su búsqueda del legendario "Atlantis de las Arenas", enfrentándose a enemigos y desafíos en ubicaciones exóticas y peligrosas alrededor del mundo.',
        'precio': 19990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 20,
        'imagen': 'productos/uncharted3.jpeg'
    },
    {
        'id': 11,
        'categoria': Categoria.objects.get(id=2),
        'nombre': 'Assassin\'s Creed Shadows',
        'descripcion': 'Ambientado en el Japón del siglo XVI, hacia el final del período Sengoku, el juego se centrará en la lucha milenaria entre la Hermandad de Asesinos, que lucha por la paz y la libertad, y la Orden de los Templarios, que desea la paz a través del control. La historia se desarrollará desde la perspectiva de dos protagonistas: Naoe, una shinobi, y Yasuke, un samurai.',
        'precio': 29990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 10,
        'imagen': 'productos/assassins_creed_shadows.png'
    },
    {
        'id': 12,
        'categoria': Categoria.objects.get(id=2),
        'nombre': 'Tomb Raider',
        'descripcion': 'Únete a Lara Croft en Tomb Raider, donde explorarás tumbas antiguas y resolverás enigmas mortales en busca de reliquias legendarias. Sobrevive a peligrosas trampas y enemigos letales en este emocionante juego de acción y aventura.',
        'precio': 19990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 15,
        'imagen': 'productos/tomb_raider.jpg'
    },
    # Categoría "Estrategia" (4 juegos)
    {
        'id': 13,
        'categoria': Categoria.objects.get(id=3),
        'nombre': 'Age of Empires II',
        'descripcion': 'Construye un imperio en Age of Empires II, donde expandirás tu civilización desde la Edad Media hasta la Edad Imperial. Investiga nuevas tecnologías, negocia con tus enemigos y domina el mundo en este juego de estrategia.',
        'precio': 9990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 5,
        'imagen': 'productos/aoe2.jpg'
    },
    {
        'id': 14,
        'categoria': Categoria.objects.get(id=3),
        'nombre': 'XCOM 2',
        'descripcion': 'Únete a la resistencia en XCOM 2, donde liderarás fuerzas de combate contra la invasión alienígena y liberarás a la Tierra de la dominación extraterrestre. Reconstruye bases secretas, investiga tecnología alienígena y lucha por la supervivencia humana.',
        'precio': 5990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 10,
        'imagen': 'productos/xcom-2.png'
    },
    {
        'id': 15,
        'categoria': Categoria.objects.get(id=3),
        'nombre': 'Civilization VI: New Frontiers',
        'descripcion': 'Civilization VI: New Frontiers es un juego de estrategia por turnos desarrollado por Firaxis Games y publicado por 2K Games. Sumérgete en un mundo de historia, exploración, diplomacia y conquista mientras construyes tu civilización desde la Edad de Piedra hasta la era espacial. Utiliza tácticas avanzadas, negocia con líderes históricos y gestiona recursos para convertirte en el líder mundial más poderoso.',
        'precio': 4990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 15,
        'imagen': 'productos/civilization.png'
    },
    {
        'id': 16,
        'categoria': Categoria.objects.get(id=3),
        'nombre': 'Total War: Empire',
        'descripcion': 'Lidera ejércitos en Total War: Empire, donde conquistarás imperios y expandirás tu influencia en guerras épicas. Utiliza tácticas militares y estrategias políticas para dominar el mundo conocido en este juego de estrategia histórica.',
        'precio': 69990,
        'descuento_subscriptor': 5,
        'descuento_oferta': 20,
        'imagen': 'productos/totalwar.jpg'
    }
    ]

    print('Crear productos')
    for producto in productos_data:
        Producto.objects.create(**producto)
    print('Productos creados correctamente')

    print('Crear carritos')
    for rut in ['19659195-8', '20377842-2']:
        cliente = Perfil.objects.get(rut=rut)
        for cantidad_productos in range(1, 11):
            producto = Producto.objects.get(pk=randint(1, 10))
            if cliente.subscrito:
                descuento_subscriptor = producto.descuento_subscriptor
            else:
                descuento_subscriptor = 0
            descuento_oferta = producto.descuento_oferta
            descuento_total = descuento_subscriptor + descuento_oferta
            descuentos = int(round(producto.precio * descuento_total / 100))
            precio_a_pagar = producto.precio - descuentos
            Carrito.objects.create(
                cliente=cliente,
                producto=producto,
                precio=producto.precio,
                descuento_subscriptor=descuento_subscriptor,
                descuento_oferta=descuento_oferta,
                descuento_total=descuento_total,
                descuentos=descuentos,
                precio_a_pagar=precio_a_pagar
            )
    print('Carritos creados correctamente')

    print('Crear boletas')
    nro_boleta = 0
    perfiles_cliente = Perfil.objects.filter(tipo_usuario='Cliente')
    for cliente in perfiles_cliente:
        estado_index = -1
        for cant_boletas in range(1, randint(6, 21)):
            nro_boleta += 1
            estado_index += 1
            if estado_index > 3:
                estado_index = 0
            estado = Boleta.ESTADO_CHOICES[estado_index][1]
            fecha_venta = date(2023, randint(1, 5), randint(1, 28))
            fecha_despacho = fecha_venta + timedelta(days=randint(0, 3))
            fecha_entrega = fecha_despacho + timedelta(days=randint(0, 3))
            if estado == 'Anulado':
                fecha_despacho = None
                fecha_entrega = None
            elif estado == 'Vendido':
                fecha_despacho = None
                fecha_entrega = None
            elif estado == 'Despachado':
                fecha_entrega = None
            boleta = Boleta.objects.create(
                nro_boleta=nro_boleta, 
                cliente=cliente,
                monto_sin_iva=0,
                iva=0,
                total_a_pagar=0,
                fecha_venta=fecha_venta,
                fecha_despacho=fecha_despacho,
                fecha_entrega=fecha_entrega,
                estado=estado)
            detalle_boleta = []
            total_a_pagar = 0
            for cant_productos in range(1, randint(4, 6)):
                producto_id = randint(1, 10)
                producto = Producto.objects.get(id=producto_id)
                precio = producto.precio
                descuento_subscriptor = 0
                if cliente.subscrito:
                    descuento_subscriptor = producto.descuento_subscriptor
                descuento_oferta = producto.descuento_oferta
                descuento_total = descuento_subscriptor + descuento_oferta
                descuentos = int(round(precio * descuento_total / 100))
                precio_a_pagar = precio - descuentos
                bodega = Bodega.objects.create(producto=producto)
                DetalleBoleta.objects.create(
                    boleta=boleta,
                    bodega=bodega,
                    precio=precio,
                    descuento_subscriptor=descuento_subscriptor,
                    descuento_oferta=descuento_oferta,
                    descuento_total=descuento_total,
                    descuentos=descuentos,
                    precio_a_pagar=precio_a_pagar)
                total_a_pagar += precio_a_pagar
            monto_sin_iva = int(round(total_a_pagar / 1.19))
            iva = total_a_pagar - monto_sin_iva
            boleta.monto_sin_iva = monto_sin_iva
            boleta.iva = iva
            boleta.total_a_pagar = total_a_pagar
            boleta.fecha_venta = fecha_venta
            boleta.fecha_despacho = fecha_despacho
            boleta.fecha_entrega = fecha_entrega
            boleta.estado = estado
            boleta.save()
            print(f'    Creada boleta Nro={nro_boleta} Cliente={cliente.usuario.first_name} {cliente.usuario.last_name}')
    print('Boletas creadas correctamente')

    print('Agregar productos a bodega')
    for producto_id in range(1, 11):
        producto = Producto.objects.get(id=producto_id)
        cantidad = 0
        for cantidad in range(1, randint(2, 31)):
            Bodega.objects.create(producto=producto)
        print(f'    Agregados {cantidad} "{producto.nombre}" a la bodega')
    print('Productos agregados a bodega')


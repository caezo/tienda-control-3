  $(document).ready(function() {
    // Método para validar RUT chileno
    $.validator.addMethod("rutChileno", function(value, element) {
        var rutPattern = /^\d{7,8}-[\dK]$/;
        if (!rutPattern.test(value)) {
            return false;
        }
        var rutSinGuion = value.replace("-", "");
        var rut = rutSinGuion.slice(0, -1);
        var dv = rutSinGuion.slice(-1);
        var factor = 2;
        var sum = 0;
        for (var i = rut.length - 1; i >= 0; i--) {
            sum += parseInt(rut.charAt(i)) * factor;
            factor = factor === 7 ? 2 : factor + 1;
        }
        var dvCalculado = 11 - (sum % 11);
        dvCalculado = dvCalculado === 11 ? "0" : dvCalculado === 10 ? "K" : dvCalculado.toString();
        return dv === dvCalculado;
    }, "El RUT no es válido (escriba sin puntos y con guión)");


    $(document).ready(function() {
      // Función para limpiar el formulario al hacer clic en el botón de limpiar
      $('#limpiar_formulario').click(function() {
          $('#form')[0].reset();  // Resetea el formulario con ID 'form'
          $('#cuadro-imagen').attr('src', '{% static "core/img/sin-imagen.png" %}');  // Restablece la imagen de perfil a la imagen predeterminada
      });
    // Método para validar correo electrónico completo
    $.validator.addMethod("emailCompleto", function(value, element) {
        var regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z\-0-9]{2,}))$/;
        return regex.test(value);
    }, 'El formato del correo no es válido');

    // Método para requerir al menos una opción seleccionada en un grupo
    $.validator.addMethod("requireGroup", function(value, element, options) {
        var groupName = options.groupName;
        return $("input[name='" + groupName + "']:checked").length > 0;
    }, "Por favor seleccione una opción.");

    // Método para validar solo letras
    $.validator.addMethod("soloLetras", function(value, element) {
        return this.optional(element) || /^[a-zA-Z\s]+$/.test(value);
    }, "Por favor ingrese sólo letras");

    // Método para validar solo números
    $.validator.addMethod("soloNumeros", function(value, element) {
        return this.optional(element) || /^[0-9]+$/.test(value);
    }, "Por favor ingrese sólo números");
    
    $('#id_rut').on('keyup', function(e) {
        e.target.value = e.target.value.toUpperCase();
    });

    // Asignar placeholders para ayudar a los usuarios
    $('#id_username').attr('placeholder', 'Ej: cgomezv, cevans, sjohasson');
    $('#id_first_name').attr('placeholder', 'Ej: Cristián, Chris, Scarlett');
    $('#id_last_name').attr('placeholder', 'Ej: Gómez Vega, Evans, Johansson');   
    $('#id_email').attr('placeholder', 'Ej: cevans@marvels.com');
    $('#id_rut').attr('placeholder', 'Ej: 11111111-1 (sin puntos y con guión)');
    $('#id_direccion').attr('placeholder', 'Calle, n° casa o edificio, n° departamento o piso\n'
        + 'localidad o ciudad, código postal o de área\n'
        + 'estado o provincia, ciudad, país');

    // Validación por defecto para campos requeridos
    $.extend($.validator.messages, {
        required: "Este campo es requerido",
    });

    // Configuración de validación del formulario
    $('#form').validate({ 
        rules: {
            'username': {
                required: true
            },
            'first_name': {
                required: true,
                soloLetras: true
            },
            'last_name': {
                required: true,
                soloLetras: true
            },
            'email': {
                required: true,
                emailCompleto: true
            },
            'password1': {
                required: true,
                minlength: 8
            },
            'password2': {
                required: true,
                equalTo: "#id_password1"
            },
            'rut': {
                required: true,
                rutChileno: true
            },
            'direccion': {
                required: true
            },
        },
        messages: {
            'username': {
                required: 'Debe ingresar un nombre de usuario',
            },
            'first_name': {
                required: 'Debe ingresar su nombre',
                soloLetras: "El nombre sólo puede contener letras y espacios en blanco",
            },
            'last_name': {
                required: 'Debe ingresar sus apellidos',
                soloLetras: "Los apellidos sólo pueden contener letras y espacios en blanco",
            },
            'email': {
                required: 'Debe ingresar su correo',
                emailCompleto: 'El formato del correo no es válido',
                email: 'Por favor, introduce una dirección de correo electrónico válida.'
            },
            'password1': {
                required: 'Debe ingresar una contraseña',
                minlength: 'La contraseña debe tener al menos 8 caracteres',
            },
            'password2': {
                required: 'Debe confirmar su contraseña',
                equalTo: 'Las contraseñas no coinciden',
            },
            'rut': {
                required: 'Debe ingresar su RUT',
                rutChileno: 'El formato del RUT no es válido',
            },
            'direccion': {
                required: 'Debe ingresar su dirección',
            },
        },
        errorPlacement: function(error, element) {
            error.insertAfter(element); // Inserta el mensaje de error después del elemento
            error.addClass('error-message'); // Aplica una clase al mensaje de error
        },
    });

    $('#crear_usuario_prueba').click(function(event) {
        event.preventDefault();
        $.get('https://randomuser.me/api/?results=1', // API para obtener datos de usuario al azar
            function(data){
                $.each(data.results, function(i, item) { // Recorrer las filas devueltas por la API

                    $('#limpiar_formulario').click();

                    $('#id_username').val(item.login.username);
                    $('#id_first_name').val(item.name.first);
                    $('#id_last_name').val(item.name.last);
                    $('#id_email').val(item.email);
                    $('#id_rut').val('11.111.111-1');
                    let dir = `${item.location.street.number} ${item.location.street.name}\n${item.location.city}\n${item.location.country}`;
                    $('#id_direccion').val(dir);
                    $('#id_subscrito').prop('checked', true);
                    $('#id_imagen').val('');
                    $('#id_password1').val('Duoc@123');
                    $('#id_password2').val('Duoc@123');   

                    Swal.fire({
                        title: 'Se ha creado un nuevo usuario de prueba',
                        html: 
                            `Se ha llenado el formulario con 
                            los datos de un usuario de prueba al azar, con la password 
                            por defecto: <br><br> <strong> "Duoc@123" </strong> <br><br>Si lo deseas puedes 
                            seleccionar una imagen de perfil y registrar este nuevo 
                            usuario presionando el botón <br><br> <strong> "Registarme" </strong>.`,
                        showClass: {
                            popup: 'animate__animated animate__fadeInDown'
                        },
                        hideClass: {
                            popup: 'animate__animated animate__fadeOutUp'
                        }
                    });
                });
            }
        );
    });
});

  
  })

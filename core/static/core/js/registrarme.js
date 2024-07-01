$(document).ready(function() {

  $.validator.addMethod("rutChileno", function(value, element) {

    // Validar que el RUT tenga el formato correcto (8 o 9 dígitos + guión + dígito verificador)
    var rutPattern = /^\d{7,8}-[\dK]$/;
    if (!rutPattern.test(value)) {
        return false;
    }

    // Validar el dígito verificador
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

// Agregar método de validación para correo
$.validator.addMethod("emailCompleto", function(value, element) {

    // Expresión regular para validar correo electrónico
    var regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z\-0-9]{2,}))$/;

    // Validar correo electrónico con la expresión regular
    return regex.test(value);

}, 'El formato del correo no es válido');

$.validator.addMethod("requireGroup", function(value, element, options) {
    var groupName = options.groupName;
    return $("input[name='" + groupName + "']:checked").length > 0;
}, "Por favor seleccione una opción.");

$.validator.addMethod("soloLetras", function(value, element) {
    return this.optional(element) || /^[a-zA-Z\s]+$/.test(value);
}, "Por favor ingrese sólo letras");

$.validator.addMethod("soloNumeros", function(value, element) {
    return this.optional(element) || /^[0-9]+$/.test(value);
}, "Por favor ingrese sólo números");

document.getElementById('rut').addEventListener('keyup', function(e) {
    e.target.value = e.target.value.toUpperCase();
});
  // Asignar placeholders para ayudar a los usuarios
  // $('#id_username').attr('placeholder', 'Ej: cgomezv, cevans, sjohasson');
  // $('#id_first_name').attr('placeholder', 'Ej: Cristián, Chris, Scarlett');
  // $('#id_last_name').attr('placeholder', 'Ej: Gómez Vega, Evans, Johansson');
  // $('#id_email').attr('placeholder', 'Ej: cevans@marvels.com');
  // $('#id_password1').attr('placeholder', '8 caracteres como mínimo');
  // $('#id_password2').attr('placeholder', 'Repetir la contraseña escogida');
  // $('#id_rut').attr('placeholder', 'Ej: 11111111-1 (sin puntos y con guión)');
  // $('#id_direccion').attr('placeholder', 'Calle, n° casa o edificio, n° departamento o piso\n'
  //   + 'localidad o ciudad, código postal o de área\n'
  //   + 'estado o provincia, ciudad, país');

  // Agregar una validación por defecto para que la imagen la exija como campo obligatorio
  // $.extend($.validator.messages, {
  //   required: "Este campo es requerido",
  // });

  $('#form').validate({ 
    rules: {
      rut: {
          required: true,
          rutChileno: true
      },
      nombre:{
          required: true,
          soloLetras: true,
      },
      apellido:{
          required: true,
          soloLetras: true,
      },
      correo:{
          required: true,
          emailCompleto: true,
      },
      direccion:{
          required: true,
      },
      password: {
          required: true,
          minlength: 5,
          maxlength: 15,
      },
      password2: {
          required: true,
          equalTo: "#password",
      },
  }, // --> Fin de reglas
  messages: {
      rut: {
          required: "El RUT es un campo obligatorio",
          rutChileno: "El formato del RUT no es válido"
      },
      nombre:{
          required: "El Nombre es un campo obligatorio",
      },
      apellido:{
          required: "El Apellido es un campo obligatorio",
      },
      correo: {
          required: "El Email es un campo obligatorio",
          emailCompleto: "El email no cumple el formato de un correo",
      },
      direccion:{
          required: "La Dirección es un campo obligatorio",
      },
      password:{
          required: "La Contraseña es un campo obligatorio",
          minlength: "Mínimo 5 caracteres",
          maxlength: "Máximo 15 caracteres"
      },
      password2: {
          required: "Repita la contraseña anterior",
          equalTo: "Debe ser igual al campo contraseña",
      },

  },
      errorPlacement: function(error, element) {
        error.insertAfter(element); // Inserta el mensaje de error después del elemento
        error.addClass('error-message'); // Aplica una clase al mensaje de error
      },
  });

  // CREAR USUARIO DE PRUEBA: Esta función permite crear un usuario de prueba usando 
  // la API "randomuser" mientras se está programando la aplicación, pero se debe
  // quitar en la versión final.
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
          dir = `${item.location.street.number} ${item.location.street.name}\n${item.location.city}\n${item.location.country}`;
          $('#id_direccion').val(dir);
          $('#id_subscrito').val(true);
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
          })

        });
      });
  });

});
  // Evento de cambio de checkbox
  var form = document.getElementById('editUsersForm');

  $('input[type="checkbox"][name="players"]').change(function() {
    // Desmarca todos los demás checkboxes
    $('input[type="checkbox"][name="players"]').not(this).prop('checked', false);
   
  });

function delete_info(form_path){
  $('#userId').val("");
  $('#email').val("");
  $('#firstName').val("");
  // Actualiza la imagen de perfil si está disponible
  $('#profileImage').attr('src', '');
  //Si se va a crear un nuevo usuario el form debe enviar a otra ruta:

  form.action = form_path;
}  

function select_user(userId){
  
  $.ajax({
    url: '/user/' + userId + '/data',
    type: 'GET',
    success: response => {
      console.log('Datos del usuario:', response);
  
      // Actualizar el formulario con los datos del usuario
      $('#userId').val(response.user_id);
      $('#email').val(response.email);
      $('#firstName').val(response.first_name);
      // Actualiza la imagen de perfil si está disponible
      $('#profileImage').attr('src', '/static/images/' + response.user_id + '/' + response.photo);
      form.action = ""
    // Actualiza el título del modal con el nombre del usuario
    $('#exampleModalLongTitle').text('Borrar ' + response.first_name);
    // Actualiza el texto del cuerpo del modal
    $('#delete-user .modal-body').text('¿Deseas borrar el usuario ' + response.first_name + '?');
    // Actualiza el atributo onclick del botón "Confirmar" con el ID del usuario
    $('#delete-user .modal-footer button[data-dismiss="modal"]').attr('onclick', 'delete_user(' + response.user_id + ')');

    },
    error: function(xhr, status, error) {
      console.error('Error al obtener los datos del usuario:', error);
      // Aquí podrías mostrar un mensaje de error al usuario
    }
  });
}

function delete_user(userId) {
  fetch("/delete-user", {
    method: "POST",
    body: JSON.stringify({ userId: userId }),
  }).then(response => {
    if (response.ok) {
      window.location.href = "/dashboard/edit-users";
      // Si la respuesta del servidor es satisfactoria, realiza alguna acción en el cliente.
      console.log('Usuario eliminado con éxito.');
    } else {
      // Si la respuesta del servidor es errónea, maneja el error en el cliente.
      console.error('Error al actualizar la ronda:', response.status);
    }
  })
  .catch(error => {
    // Si hay algún error en la solicitud, maneja el error en el cliente.
    console.error('Error en la solicitud:', error);
  });
}


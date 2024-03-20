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
    },
    error: function(xhr, status, error) {
      console.error('Error al obtener los datos del usuario:', error);
      // Aquí podrías mostrar un mensaje de error al usuario
    }
  });
}


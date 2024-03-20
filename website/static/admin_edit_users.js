  // Evento de cambio de checkbox
  var form = document.getElementById('editUsersForm');

  $('input[type="checkbox"][name="players"]').change(function() {
    // Desmarca todos los demás checkboxes
    $('input[type="checkbox"][name="players"]').not(this).prop('checked', false);
    form.action = null
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



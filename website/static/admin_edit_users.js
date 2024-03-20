  // Evento de cambio de checkbox
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
  var form = document.getElementById('editUsersForm');
  form.action = form_path;
}  



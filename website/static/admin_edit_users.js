  // Evento de cambio de checkbox
  $('input[type="checkbox"][name="players"]').change(function() {
    // Desmarca todos los demás checkboxes
    $('input[type="checkbox"][name="players"]').not(this).prop('checked', false);
  });

function delete_info(){
  $('#userId').val("");
  $('#email').val("");
  $('#firstName').val("");
  // Actualiza la imagen de perfil si está disponible
  if (response.photo) {
    $('#profileImage').attr('src', '');
  }
  //Si se va a crear un nuevo usuario el form debe enviar a otra ruta:
  var form = document.getElementById('editUsersForm');
  form.action = "{{ url_for('views.edit_users') }}";
}  



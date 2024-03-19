$(".winrate").each(function() {
  contenido = parseInt($(this).html());
  if (contenido > 80) {
    $(this).css("color", "#33FF33");
    $(this).next().css("color", "#33FF33");
  } else if (contenido> 50) {
    $(this).css("color", "#66CC33");
    $(this).next().css("color", "#66CC33");
  }
    else if (contenido > 25){
      $(this).css("color", "#99FF33");
      $(this).next().css("color", "#99FF33");
  }
    else{
      $(this).css("color", "red");
      $(this).next().css("color", "red");
    }
      
});

function tournaments(userId, year){
  $.ajax({
      url: `/user/${userId}/data`,
      type: 'GET',
      data: { year: year },
      dataType: 'json',
      success: (data)=> {
        let gamesPlayedList = $('#games_played_by_'+ userId);
        gamesPlayedList.empty();
        for (const game of data.game_played) {
          gamesPlayedList.append(`                        
          <a href="" class="text-decoration-none text-dark" data-toggle="modal" data-target="#game-${game.id}">
          <li>${game.place}</li>
          </a>`);
        }
      },
      error: (xhr, status, error)=> {
          console.log(xhr.responseText);
      }
  });
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
        if (response.photo) {
          $('#profileImage').attr('src', '/static/images/' + response.user_id + '/' + response.photo);
        }
      },
      error: function(xhr, status, error) {
        console.error('Error al obtener los datos del usuario:', error);
        // Aquí podrías mostrar un mensaje de error al usuario
      }
    });
  }




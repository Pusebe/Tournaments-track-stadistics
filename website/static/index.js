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





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

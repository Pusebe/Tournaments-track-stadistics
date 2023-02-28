function delete_round(roundsId) {
  fetch("/delete-round", {
    method: "POST",
    body: JSON.stringify({ roundsId: roundsId }),
  }).then(response => {
    if (response.ok) {
      window.location.href = "/dashboard/games";
      // Si la respuesta del servidor es satisfactoria, realiza alguna acción en el cliente.
      console.log('Ronda Borrada exitosamente.');
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

function delete_game(gameId) {
  fetch("/delete-game", {
    method: "POST",
    body: JSON.stringify({ gameId: gameId }),
  }).then(response => {
    if (response.ok) {
      window.location.href = "/dashboard/games";
      // Si la respuesta del servidor es satisfactoria, realiza alguna acción en el cliente.
      console.log('Ronda Borrada exitosamente.');
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
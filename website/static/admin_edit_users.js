  // Evento de cambio de checkbox
  $('input[type="checkbox"][name="players"]').change(function() {
    // Desmarca todos los demás checkboxes
    $('input[type="checkbox"][name="players"]').not(this).prop('checked', false);
  });


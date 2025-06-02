// JavaScript para la página de convocatorias

// Manejo del formulario de creación de convocatorias
function initializeConvocatoriaForm() {
  const form = document.getElementById('createConvocatoriaForm');
  
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formData = new FormData(e.target);
      const checkboxes = document.querySelectorAll('input[name="players"]:checked');
      
      // Añadir todos los jugadores seleccionados al FormData
      checkboxes.forEach(checkbox => {
        formData.append('players', checkbox.value);
      });
      
      try {
        const response = await fetch(e.target.action, {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          window.location.reload();
        } else {
          const data = await response.json();
          alert(`Error: ${data.error}`);
        }
      } catch (error) {
        console.error('Error al crear la convocatoria:', error);
        alert('Error al crear la convocatoria. Por favor, inténtalo de nuevo.');
      }
    });
  }
}

// Función para compartir por WhatsApp
function initializeWhatsAppSharing() {
  document.addEventListener('click', function(e) {
    if (e.target.closest('.whatsapp-share-btn')) {
      e.preventDefault();
      
      const btn = e.target.closest('.whatsapp-share-btn');
      const subject = btn.dataset.subject;
      const date = btn.dataset.date;
      const place = btn.dataset.place;
      const link = btn.dataset.link;
      const invitedCount = btn.dataset.invitedCount;
      
      // Crear el mensaje bonito para WhatsApp
      const message = createWhatsAppMessage(subject, date, place, link);
      
      // Crear la URL de WhatsApp
      const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
      
      // Abrir WhatsApp en una nueva ventana
      window.open(whatsappUrl, '_blank');
    }
  });
}

// Función para crear el mensaje de WhatsApp
function createWhatsAppMessage(subject, date, place, link) {
  return `${subject}

📅 ${date}

📍 ${place}

Confirma tu asistencia aquí: 
${link}`;
}

// Función para inicializar efectos visuales de selección
function initializePlayerSelection() {
  const checkboxes = document.querySelectorAll('.player-checkbox');
  
  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
      const img = this.nextElementSibling;
      
      if (this.checked) {
        img.style.filter = 'grayscale(0%)';
        img.style.backgroundColor = '#007bff';
      } else {
        img.style.filter = 'grayscale(100%)';
        img.style.backgroundColor = '';
      }
    });
  });
}

// Inicializar todo cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  initializeConvocatoriaForm();
  initializeWhatsAppSharing();
  initializePlayerSelection();
});
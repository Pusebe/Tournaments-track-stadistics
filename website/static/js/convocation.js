// Configuración de OneSignal y manejo de la convocatoria

// Inicialización de OneSignal
window.OneSignalDeferred = window.OneSignalDeferred || [];

// Función para enviar onesignal_id al cargar la página
function sendOnesignalIdToBackend(onesignalId) {
  if (onesignalId) {
    // Recargar la página con el onesignal_id como parámetro
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('onesignal_id', onesignalId);
    
    // Solo recargar si no está ya el parámetro para evitar bucle infinito
    if (!window.location.search.includes('onesignal_id=')) {
      window.location.href = currentUrl.toString();
    }
  }
}

// Ocultar overlay después de un momento
function hideLoadingOverlay() {
  setTimeout(() => {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
      overlay.style.opacity = '0';
      overlay.style.transition = 'opacity 0.6s ease';
      
      // Remover completamente el overlay después de la transición
      setTimeout(() => {
        overlay.style.display = 'none';
      }, 600);
    }
  }, 800);
}

// Función para intentar obtener el ID con reintentos
async function getOnesignalIdWithRetry(maxRetries = 10, delay = 200) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const subscriptionId = await OneSignal.User.PushSubscription.id;
      if (subscriptionId) {
        return subscriptionId;
      }
    } catch (error) {
      console.log(`Intento ${i + 1}: OneSignal ID no disponible aún`);
    }
    
    // Esperar antes del siguiente intento
    await new Promise(resolve => setTimeout(resolve, delay));
  }
  return null;
}

// Configuración de OneSignal
OneSignalDeferred.push(function (OneSignal) {
  OneSignal.init({
    appId: "2775bcd1-0a9c-40e1-99e8-e325e6b20769",
    autoResubscribe: true,
    welcomeNotification: {"disable": true},
    notifyButton: { enable: false }
  });

  // Obtener el onesignal_id tan pronto como esté disponible
  getOnesignalIdWithRetry().then(onesignalId => {
    if (onesignalId) {
      sendOnesignalIdToBackend(onesignalId);
    }
  });

  // También escuchar cambios por si acaso
  OneSignal.User.PushSubscription.addEventListener('change', async (event) => {
    const subscriptionId = await OneSignal.User.PushSubscription.id;
    if (subscriptionId) {
      sendOnesignalIdToBackend(subscriptionId);
    }
  });
});

// Manejo de selección de imágenes
function initializeImageSelection() {
  const userRadios = document.querySelectorAll('input[name="user_id"]');
  if (userRadios.length > 0) {
    userRadios.forEach(radio => {
      radio.addEventListener('change', () => {
        document.querySelectorAll('.round-img').forEach(img => {
          img.style.filter = 'grayscale(100%)';
          img.style.backgroundColor = '';
        });
        if (radio.checked) {
          const img = radio.nextElementSibling;
          img.style.filter = 'grayscale(0%)';
          img.style.backgroundColor = '#007bff';
        }
      });
    });
  }
}

// Manejo del formulario de confirmación
function initializeFormHandler() {
  const form = document.getElementById('joinConvocationForm');
  
  // Verificar si el usuario ya está confirmado usando los datos pasados desde Flask
  const userAlreadyConfirmed = window.convocationData && window.convocationData.userAlreadyConfirmed;
  
  if (form && !userAlreadyConfirmed) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const selectedUser = document.querySelector('input[name="user_id"]:checked');

      if (!selectedUser) {
        alert("Por favor, selecciona un usuario.");
        return;
      }

      const userId = selectedUser.value;
      let notificationsAccepted = false;

      OneSignalDeferred.push(async function (OneSignal) {
        try {
          if (typeof OneSignal.User.setExternalId === "function") {
            await OneSignal.User.setExternalId(userId);
          } else {
            console.warn("setExternalId no está disponible");
          }

          // Verificar si ya está suscrito
          let isOptedIn = await OneSignal.User.PushSubscription.optedIn;
          
          if (!isOptedIn) {
            try {
              // Intentar solicitar permisos
              await OneSignal.User.PushSubscription.optIn();
              // Verificar nuevamente después de la solicitud
              isOptedIn = await OneSignal.User.PushSubscription.optedIn;
              notificationsAccepted = isOptedIn;
            } catch (optInError) {
              console.log("Usuario rechazó o no pudo otorgar permisos de notificación");
              notificationsAccepted = false;
            }
          } else {
            notificationsAccepted = true;
          }

          // Obtener tokens si están disponibles y agregarlos al formulario
          try {
            const pushToken = await OneSignal.User.PushSubscription.token;
            if (pushToken) {
              // Crear input hidden para el token
              const tokenInput = document.createElement('input');
              tokenInput.type = 'hidden';
              tokenInput.name = 'push_token';
              tokenInput.value = pushToken;
              form.appendChild(tokenInput);
            }

            const subscriptionId = await OneSignal.User.PushSubscription.id;
            if (subscriptionId) {
              // Crear input hidden para el onesignal_id
              const idInput = document.createElement('input');
              idInput.type = 'hidden';
              idInput.name = 'onesignal_id';
              idInput.value = subscriptionId;
              form.appendChild(idInput);
              console.log("Subscription ID:", subscriptionId);
            }
          } catch (tokenError) {
            console.log("No se pudieron obtener los tokens de notificación");
          }

          // Mostrar mensaje sobre notificaciones si no se aceptaron
          if (!notificationsAccepted) {
            alert("¡Tu registro se procesará correctamente!\n\nNota: No verás cambios en tiempo real hasta que aceptes las notificaciones. Puedes habilitarlas en cualquier momento desde la configuración de tu navegador.");
          }

          // Enviar el formulario de forma normal (no AJAX)
          // Esto permite que Flask maneje los redirects y flash messages
          form.submit();
          
        } catch (err) {
          console.error("Error con OneSignal:", err);
          
          // Aun con errores de OneSignal, enviar el formulario
          alert("Las notificaciones no pudieron configurarse, pero tu registro se procesará correctamente.\n\nPuedes habilitar las notificaciones desde la configuración de tu navegador.");
          form.submit();
        }
      });
    });
  }
}

// Inicializar todo cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  hideLoadingOverlay();
  initializeImageSelection();
  initializeFormHandler();
});
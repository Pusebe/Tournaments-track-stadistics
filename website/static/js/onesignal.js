// static/js/onesignal.js

/**
 * Inicializa OneSignal y maneja la lógica de suscripción.
 */

const sendPlayerIdToBackend = async (playerId) => {
    if (!playerId) {
        console.warn("No Player ID to send to backend.");
        return;
    }
    console.log("Attempting to send Player ID to backend:", playerId);
    try {
        const response = await fetch('/api/user/update_onesignal_player_id', { // Endpoint del backend
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ player_id: playerId })
        });
        const responseData = await response.json();
        if (response.ok) {
            console.log("Player ID successfully sent to backend:", responseData);
        } else {
            console.error("Error sending Player ID to backend:", responseData.message || response.statusText);
        }
    } catch (error) {
        console.error("Network or other error sending Player ID:", error);
    }
};

function initializeOneSignal() {
    console.log("DEBUG: initializeOneSignal called");
    window.OneSignalDeferred = window.OneSignalDeferred || [];

    window.OneSignalDeferred.push(function(OneSignalPushed) { // NO es una función async aquí
        console.log("DEBUG: OneSignalDeferred.push callback executing.");
        console.log("DEBUG: Object received by push (OneSignalPushed):", OneSignalPushed);
        console.log("DEBUG: typeof OneSignalPushed:", typeof OneSignalPushed);

        // Usamos el objeto OneSignalPushed para init
        OneSignalPushed.init({
            appId: "2775bcd1-0a9c-40e1-99e8-e325e6b20769",
            notifyButton: {
                enable: true,
            },
            allowLocalhostAsSecureOrigin: true,
        }).then(function() {
            // Este .then() se ejecuta DESPUÉS de que init() haya terminado y resuelto exitosamente
            console.log("OneSignal SDK Initialized (SUCCESS via .then()).");

            // En este punto, window.OneSignal DEBERÍA ser la instancia API completamente funcional
            console.log("DEBUG: window.OneSignal (inside .then() after init):", window.OneSignal);
            console.log("DEBUG: typeof window.OneSignal (inside .then()):", typeof window.OneSignal);
            console.log("DEBUG: typeof window.OneSignal.on (inside .then()):", typeof window.OneSignal.on);

            if (typeof window.OneSignal.on !== 'function') {
                console.error("CRITICAL ERROR (in .then()): window.OneSignal.on is STILL not a function.");
                return; // Salir si el SDK sigue sin estar bien
            }

            // A partir de aquí, usa window.OneSignal para todas las operaciones
            const OS = window.OneSignal;

            OS.on('subscriptionChange', async function(isSubscribed) {
                console.log("OneSignal subscription changed. Is subscribed:", isSubscribed);
                if (isSubscribed) {
                    const playerId = await OS.getPlayerId();
                    console.log("New OneSignal Player ID:", playerId);
                    await sendPlayerIdToBackend(playerId);
                } else {
                    console.log("User is no longer subscribed to OneSignal.");
                }
            });

            return OS.isPushNotificationsEnabled(); // Devolvemos la promesa para encadenar
        }).then(function(isSubscribed) {
            // Este .then() se ejecuta después de isPushNotificationsEnabled()
            // isSubscribed puede ser undefined si el .then() anterior salió por el error crítico
            if (typeof isSubscribed === "boolean") {
                console.log("Initial OneSignal subscription status (via .then()):", isSubscribed);
                if (isSubscribed) {
                    return window.OneSignal.getPlayerId().then(function(playerId) {
                        if (playerId) {
                            console.log("User already subscribed. Player ID (via .then()):", playerId);
                            return sendPlayerIdToBackend(playerId); // Devuelve la promesa de sendPlayerIdToBackend
                        }
                    });
                } else {
                    console.log("User not subscribed. OneSignal will prompt if configured.");
                }
            }
        }).catch(function(error) {
            // Este .catch() atrapará errores de init() o de cualquiera de los .then() anteriores
            console.error("Error during OneSignal initialization or subsequent setup:", error);
        });
    });
}

// Ejecutar la inicialización cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeOneSignal);
} else {
    initializeOneSignal();
}
// Fonction principale pour obtenir la position
function getUserLocation(callbackSuccess, callbackError) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => callbackSuccess(position.coords),
            error => callbackError(error)
        );
    } else {
        callbackError({ code: 0, message: "La géolocalisation n'est pas supportée par ce navigateur." });
    }
}

// Fonction pour envoyer la position au serveur
function sendToServer(latitude, longitude, callback) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    fetch('/etablissements_proches', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ latitude, longitude }),
    })
    .then(response => response.json())
    .then(data => callback(data))
    .catch(error => console.error('Error:', error));
}

// Export des fonctions pour les utiliser dans d'autres fichiers
window.geoloc = {
    getUserLocation,
    sendToServer
};

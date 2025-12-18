function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("La géolocalisation n'est pas supportée par ce navigateur.");
    }
}

function showPosition(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    sendToServer(latitude, longitude);
}

function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert("L'utilisateur a refusé la demande de géolocalisation.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Les informations de position sont indisponibles.");
            break;
        case error.TIMEOUT:
            alert("La demande de position a expiré.");
            break;
        case error.UNKNOWN_ERROR:
            alert("Une erreur inconnue est survenue.");
            break;
    }
}


function sendToServer(latitude, longitude) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Envoie les coordonnées au serveur pour obtenir les établissements proches
    fetch('/etablissements_proches', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ latitude, longitude }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Établissements proches :', data.etablissements);
        afficherEtablissementsProches(data.etablissements);  // Fonction à implémenter
    })
    .catch(error => console.error('Error:', error));
}




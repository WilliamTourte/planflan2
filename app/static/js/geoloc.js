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
    const data = { latitude, longitude };
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/geoloc', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    })
    .then(data => console.log('Success:', data))
    .catch(error => console.error('Error:', error));
}



let autocomplete;
let map;
let markers = [];
let infowindowContents = {};
let infowindow;
let etablissements = [];
let isAdmin = false;
let googleMapsApiKey = '';
let csrfToken = '';
let nom = '';
let visite = '';
let labellise = '';

// Fonction utilitaire pour limiter le nombre de requêtes (debounce)
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Fonction pour recharger les établissements selon les filtres
async function loadEtablissements(nom = '', visite = '', labellise = '') {
    try {
        const response = await fetch(`/api/etablissements?nom=${encodeURIComponent(nom)}&visite=${visite}&labellise=${labellise}`);
        if (!response.ok) throw new Error("Erreur lors du chargement des établissements.");
        return await response.json();
    } catch (error) {
        console.error("Erreur:", error);
        return [];
    }
}

// Fonction pour mettre à jour la carte avec de nouveaux établissements
async function updateMapAndMarkers(nom = '', visite = '', labellise = '') {
    const newEtablissements = await loadEtablissements(nom, visite, labellise);
    if (!newEtablissements || newEtablissements.length === 0) {
        console.warn("Aucun établissement trouvé avec ces filtres.");
        return;
    }

    // Effacer les anciens marqueurs
    if (map) {
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });
    }

    // Mettre à jour la variable globale
    etablissements = newEtablissements;
    const bounds = L.latLngBounds();

    // Définition des icônes personnalisées avec emojis
    const createEmojiIcon = (emoji, className) => {
        return L.divIcon({
            html: `<div class="emoji-marker ${className}">${emoji}</div>`,
            className: 'emoji-icon',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
    };
    const labelIcon = createEmojiIcon('🏆', 'label-icon');
    const visiteIcon = createEmojiIcon('✅', 'visited-icon');
    const nonvisiteIcon = createEmojiIcon('❌', 'unvisited-icon');

    // Ajout des nouveaux marqueurs
    etablissements.forEach(etablissement => {
        let icon;
        if (isAdmin) {
            if (etablissement.label) {
                icon = labelIcon;
            } else if (etablissement.visite) {
                icon = visiteIcon;
            } else {
                icon = nonvisiteIcon;
            }
        } else {
            icon = etablissement.label ? labelIcon : nonvisiteIcon;
        }
        const marker = L.marker([etablissement.latitude, etablissement.longitude], {
            icon: icon,
            title: etablissement.nom
        })
        .addTo(map)
        .bindPopup(infowindowContents[etablissement.id_etab] || "Détails non disponibles");
        bounds.extend(marker.getLatLng());
    });

    // Ajuster la vue de la carte
    if (etablissements.length > 0) {
        if (etablissements.length === 1) {
            map.setView([etablissements[0].latitude, etablissements[0].longitude], 14);
        } else {
            map.fitBounds(bounds);
        }
    }
}

// Fonction pour initialiser l'autocomplétion
window.initAutocomplete = function() {
    const input = document.getElementById('search');
    if (!input) {
        console.error("Élément #search introuvable !");
        return;
    }
    autocomplete = new google.maps.places.Autocomplete(input, {
        types: ['establishment'],
        componentRestrictions: {country: 'fr'}
    });
    // Écouter les changements dans l'Autocomplete
    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        if (!place.geometry) return;
        // Remplir les champs CACHÉS avec le préfixe "ajout-etab-"
        document.getElementById('ajout-etab-nom').value = place.name || '';
        document.getElementById('ajout-etab-adresse').value = place.formatted_address || '';
        document.getElementById('ajout-etab-latitude').value = place.geometry.location.lat();
        document.getElementById('ajout-etab-longitude').value = place.geometry.location.lng();
        // Vérifier si le lieu est déjà dans la liste
        fetch('/verifier_etablissement', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ nom: place.name }),
        })
        .then(async response => {
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Erreur serveur: ${errorText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error("Erreur:", data.error);
                return;
            }
            if (data.exists) {
                const previousMessages = document.querySelectorAll('.alert-warning');
                previousMessages.forEach(msg => msg.remove());
                const message = document.createElement('div');
                message.className = 'alert alert-warning';
                message.innerHTML = `Cet établissement est déjà dans la liste. <a href="${data.url}">Voir la page</a>`;
                document.querySelector('.form-container').prepend(message);
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            const errorMessage = document.createElement('div');
            errorMessage.className = 'alert alert-danger';
            errorMessage.textContent = `Erreur: ${error.message}`;
            document.querySelector('.form-container').prepend(errorMessage);
        });
        // Envoyer l'adresse à une route AJAX pour extraire le code postal et la ville
        fetch('/extraire_infos_adresse', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
            body: JSON.stringify({ adresse: place.formatted_address }),
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('ajout-etab-code_postal').value = data.code_postal || '';
            document.getElementById('ajout-etab-ville').value = data.ville || '';
            document.getElementById('ajout-etab-adresse').value = data.adresse_nettoyee || '';
        })
        .catch(error => console.error('Erreur:', error));
    });
};

// Fonction pour initialiser la carte
window.initMap = function() {
    const mapElement = document.getElementById("map");
    if (!mapElement) {
        console.error("Élément #map introuvable !");
        const mapContainer = document.getElementById("map-container");
        if (mapContainer) {
            mapContainer.innerHTML = "<p style='color: red;'>Erreur : Impossible de charger la carte.</p>";
        } else {
            console.error("Élément #map-container introuvable !");
        }
        return;
    }
    // Initialisation de la carte Leaflet
    map = L.map('map').setView([46.2276, 2.2137], 6);
    // Ajout de la couche OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Légende
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'info legend');
        div.style.backgroundColor = 'white';
        div.style.padding = '10px';
        div.style.margin = '10px';
        div.style.border = '1px solid #ccc';
        div.innerHTML = `🏆 Labellisé ✅ Visité ❌ Non visité`;
        return div;
    };
    legend.addTo(map);
};

// Fonction pour initialiser l'autocomplétion et la carte
window.initAll = function() {
    initAutocomplete();
    initMap();
    // Charger la carte avec les données initiales
    updateMapAndMarkers(nom, visite, labellise);
};

// Écouter les changements sur les filtres
document.addEventListener('DOMContentLoaded', function() {
    // Chargement de l'API Google Maps (uniquement pour l'autocomplete)
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&libraries=places&callback=initAll&v=weekly&loading=async`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);

    // Écouter les filtres
    const nomFilter = document.getElementById('filter-nom');
    const visiteFilter = document.getElementById('filter-visite');
    const labelliseFilter = document.getElementById('filter-labellise');

    if (nomFilter) {
        nomFilter.addEventListener('input', debounce(function() {
            updateMapAndMarkers(this.value, visiteFilter?.value, labelliseFilter?.value);
        }, 500));
    }

    if (visiteFilter) {
        visiteFilter.addEventListener('change', function() {
            updateMapAndMarkers(nomFilter?.value, this.value, labelliseFilter?.value);
        });
    }

    if (labelliseFilter) {
        labelliseFilter.addEventListener('change', function() {
            updateMapAndMarkers(nomFilter?.value, visiteFilter?.value, this.value);
        });
    }
});

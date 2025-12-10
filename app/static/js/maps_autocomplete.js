let autocomplete;
let map;
let markers = {};
let infowindowContents = {};

function closeInfoWindow() {
    // Leaflet gère la fermeture des popups automatiquement
}

// Fonction pour initialiser l'autocomplétion et la carte
window.initAll = function() {
    initAutocomplete();
    initMap();
};

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
    // Écouter la sélection d'un lieu
    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        if (!place.geometry) {
            console.error("Aucune information de géolocalisation disponible pour ce lieu.");
            return;
        }
        // Remplir les champs cachés
        document.getElementById('ajout-etab-nom').value = place.name || '';
        document.getElementById('ajout-etab-adresse').value = place.formatted_address || '';
        document.getElementById('ajout-etab-latitude').value = place.geometry.location.lat();
        document.getElementById('ajout-etab-longitude').value = place.geometry.location.lng();

        // Vérifier si le lieu est déjà dans la liste
        fetch('/verifier_etablissement', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
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
                document.querySelector('.etablissement-form-container').prepend(message);
                // Stocker l'URL pour l'utiliser dans la carte
                window.etablissementUrl = data.url;
            } else {
                window.etablissementUrl = null;
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            const errorMessage = document.createElement('div');
            errorMessage.className = 'alert alert-danger';
            errorMessage.textContent = `Erreur: ${error.message}`;
            document.querySelector('.etablissement-form-container').prepend(errorMessage);
            window.etablissementUrl = null;
        });

        // Extraire le code postal et la ville
        fetch('/extraire_infos_adresse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({ adresse: place.formatted_address }),
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('ajout-etab-code_postal').value = data.code_postal || '';
            document.getElementById('ajout-etab-ville').value = data.ville || '';
            document.getElementById('ajout-etab-adresse').value = data.adresse_nettoyee || '';
            // Afficher la carte Leaflet
            initMap(place.geometry.location.lat(), place.geometry.location.lng(), place.name);
        })
        .catch(error => console.error('Erreur:', error));
    });
};

window.initMap = function(lat, lng, title, etablissementUrl = null) {
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
    let center = [46.2276, 2.2137];
    let zoom = 6;

    // Si on a des coordonnées précises (cas de l'autocomplete), on centre dessus
    if (lat && lng) {
        center = [lat, lng];
        zoom = 15;
    }

    map = L.map('map').setView(center, zoom);

    // Ajout de la couche OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Si on a un établissement sélectionné via l'autocomplete
    if (lat && lng && title) {
        let popupContent = `<b>${title}</b>`;
        if (etablissementUrl) {
            popupContent += `<br><a href="${etablissementUrl}" target="_blank">Voir la page de l'établissement</a>`;
        }
        L.marker([lat, lng])
            .addTo(map)
            .bindPopup(popupContent)
            .openPopup();
    }

    // Chargement des établissements existants (si présent dans la page)
    const etablissementsDataElement = document.getElementById('etablissements-data');
    if (etablissementsDataElement) {
        const etablissements = JSON.parse(etablissementsDataElement.getAttribute('data-etablissements'));
        const isAdmin = JSON.parse(document.getElementById('is-admin').getAttribute('data-is-admin'));
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

        // Ajout des marqueurs avec les emojis
        etablissements.forEach(etablissement => {
            let icon;
            if (etablissement.label) {
                icon = labelIcon;
            } else if (etablissement.visite) {
                icon = visiteIcon;
            } else {
                icon = nonvisiteIcon;
            }
            const marker = L.marker([etablissement.latitude, etablissement.longitude], {
                icon: icon,
                title: etablissement.nom,
                id_etab: etablissement.id_etab
            })
            .addTo(map)
            .on('click', function(e) {
                // Charger le contenu de l'infowindow à la demande
                if (!this.getPopup()) {
                    this.bindPopup("Chargement en cours...").openPopup();
                    fetch(`/get_infowindow_content?id_etab=${etablissement.id_etab}`)
                        .then(response => response.text())
                        .then(content => {
                            this.setPopupContent(content);
                        })
                        .catch(error => {
                            console.error(`Erreur lors du chargement de l'infowindow pour ${etablissement.nom}:`, error);
                            this.setPopupContent("Détails non disponibles");
                        });
                }
            });
            bounds.extend(marker.getLatLng());
        });

        // Ajustement de la vue en fonction du nombre d'établissements
        if (etablissements.length > 0) {
            if (etablissements.length === 1) {
                map.setView([etablissements[0].latitude, etablissements[0].longitude], 14);
            } else {
                map.fitBounds(bounds);
            }

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
    }
};


// Chargement de l'API Google Maps (uniquement pour l'autocomplete)
document.addEventListener('DOMContentLoaded', function() {
    const googleMapsApiKey = document.getElementById('google-maps-api-key').getAttribute('data-api-key');
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&libraries=places&callback=initAll&v=weekly`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
});

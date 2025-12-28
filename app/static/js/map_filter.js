// Variables globales
let map;
let markers = [];
let etablissements = [];
let userMarker = null;

let baseUrl = window.location.origin;
let userLocation = null;
let proximityRadius = 5;

// Variables pour les filtres
let activeFilters = {
    type_pate: false,
    visited: false,
    unvisited: false,
    label: false,
    proximity: false
};

// Fonction pour initialiser les données dynamiques
function initDataElements() {
    if (!document.getElementById('etablissements-data')) {
        const etablissementsDataElement = document.createElement('div');
        etablissementsDataElement.id = 'etablissements-data';
        etablissementsDataElement.setAttribute('data-etablissements', '[]');
        document.body.appendChild(etablissementsDataElement);
    }

    if (!document.getElementById('is-admin')) {
        const isAdminElement = document.createElement('div');
        isAdminElement.id = 'is-admin';
        isAdminElement.setAttribute('data-is-admin', 'false');
        document.body.appendChild(isAdminElement);
    }

    if (!document.getElementById('google-maps-api-key')) {
        const googleMapsApiKeyElement = document.createElement('div');
        googleMapsApiKeyElement.id = 'google-maps-api-key';
        googleMapsApiKeyElement.setAttribute('data-api-key', '');
        document.body.appendChild(googleMapsApiKeyElement);
    }

    // Récupérer la position utilisateur si disponible
    const userLocationElement = document.getElementById('user-location');
    if (userLocationElement) {
        userLocation = {
            lat: parseFloat(userLocationElement.getAttribute('data-lat')),
            lon: parseFloat(userLocationElement.getAttribute('data-lon'))
        };
        activeFilters.proximity = true;
    }
}

// Fonction pour créer des icônes personnalisées
const createEmojiIcon = (emoji, className) => {
    return L.divIcon({
        html: `<div class="emoji-marker ${className}">${emoji}</div>`,
        className: 'emoji-icon',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
};

// Fonction pour calculer la distance entre deux points (en km)
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Rayon de la Terre en km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

// Fonction pour créer un marqueur avec un popup asynchrone pour un établissement donné
function createEtablissementMarker(map, etablissement, baseUrl = window.location.origin) {
    let icon = createEmojiIcon('🏠', 'default-icon');
    if (etablissement.label) {
        icon = createEmojiIcon('❤️', 'label-icon');
    } else if (etablissement.visite) {
        icon = createEmojiIcon('✅', 'visited-icon');
    } else {
        icon = createEmojiIcon('👋', 'unvisited-icon');
    }

    const marker = L.marker(
        [etablissement.latitude, etablissement.longitude],
        { icon: icon, title: etablissement.nom }
    ).addTo(map);

    // Ne pas charger le popup immédiatement, mais seulement au clic
    marker.on('click', function() {
        if (!marker.getPopup()) {
            marker.bindPopup("Chargement en cours...");
            marker.openPopup();
            fetch(`/get_infowindow_content?id_etab=${etablissement.id_etab}`)
                .then(response => response.text())
                .then(content => {
                    marker.setPopupContent(content);
                })
                .catch(error => {
                    console.error('Erreur lors du chargement du popup:', error);
                    let popupContent = `<div class="infowindow-content"><h4>${etablissement.nom}</h4>`;
                    popupContent += `<p>${etablissement.adresse}, ${etablissement.ville}</p>`;
                    popupContent += `<a href="${baseUrl}/etablissement/${etablissement.id_etab}" class="btn btn-success">Voir plus</a></div>`;
                    marker.setPopupContent(popupContent);
                });
        } else {
            marker.openPopup();
        }
    });

    marker.options.etablissement = etablissement;
    return marker;
}


// Fonction pour mettre à jour l'affichage des marqueurs en fonction des filtres
function updateMarkersBasedOnFilters() {
    markers.forEach(marker => {
        const etablissement = marker.options.etablissement;
        let showMarker = true;

        // Filtre de proximité
        if (activeFilters.proximity && userLocation) {
            const distance = calculateDistance(
                userLocation.lat, userLocation.lon,
                etablissement.latitude, etablissement.longitude
            );
            if (distance > proximityRadius) {
                showMarker = false;
            }
        }

        // Filtre par type de pâte
        if (activeFilters.type_pate && showMarker) {
            if (!etablissement.flans || etablissement.flans.length === 0) {
                showMarker = false;
            } else {
                const hasMatchingPate = etablissement.flans.some(flan => flan.type_pate === activeFilters.type_pate);
                if (!hasMatchingPate) showMarker = false;
            }
        }

        // Autres filtres
        if (activeFilters.visited && !etablissement.visite && showMarker) showMarker = false;
        if (activeFilters.unvisited && etablissement.visite && showMarker) showMarker = false;
        if (activeFilters.label && !etablissement.label && showMarker) showMarker = false;

        if (showMarker) {
            map.addLayer(marker);
        } else {
            map.removeLayer(marker);
        }
    });
}

// Fonction pour créer un marqueur utilisateur
function createUserMarker() {
    if (userMarker) map.removeLayer(userMarker);
   

    if (userLocation) {
        userMarker = L.marker([userLocation.lat, userLocation.lon], {
            icon : createEmojiIcon('📍', 'localisation-icon')
            
        }).addTo(map);

        // Centrer la carte sur l'utilisateur
        map.setView([userLocation.lat, userLocation.lon], 13);
    }
}

// Initialisation de la carte Leaflet
function initMap() {
    const mapElement = document.getElementById("map");
    if (!mapElement) {
        console.error("Élément #map introuvable !");
        return;
    }

    // Position par défaut (centre de la France)
    let center = [46.2276, 2.2137];
    let zoom = 6;

    // Si on a une position utilisateur, centrer dessus
    if (userLocation) {
        center = [userLocation.lat, userLocation.lon];
        zoom = 13;
    }

    map = L.map('map').setView(center, zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // Ajouter le marqueur utilisateur si position disponible
    createUserMarker();

    // Légende
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'info legend');
        div.style.backgroundColor = 'white';
        div.style.padding = '5px';
        div.style.margin = '10px';
        div.style.border = '1px solid #ccc';
        div.innerHTML = `❤️ Labellisé ✅ Visité 👋 Non visité`;
        return div;
    };
    legend.addTo(map);
}

        icon = createEmojiIcon('', 'unvisited-icon');//

// Chargement des établissements
function loadEtablissements() {
    try {
        const etablissementsDataElement = document.getElementById('etablissements-data');
        if (!etablissementsDataElement) {
            console.error("Élément #etablissements-data introuvable !");
            return [];
        }
        return JSON.parse(etablissementsDataElement.getAttribute('data-etablissements'));
    } catch (error) {
        console.error("Erreur lors du chargement des établissements:", error);
        return [];
    }
}

// Mise à jour de la carte et des marqueurs
function updateMapAndMarkers() {
    etablissements = loadEtablissements();
    if (!etablissements || etablissements.length === 0) {
        console.warn("Aucun établissement trouvé.");
        return;
    }

    // Efface les anciens marqueurs
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    const bounds = L.latLngBounds();

    etablissements.forEach(etablissement => {
        if (etablissement.latitude && etablissement.longitude) {
            const marker = createEtablissementMarker(map, etablissement, false, baseUrl);
            markers.push(marker);
            bounds.extend(marker.getLatLng());
        }
    });

    // Ajuste la vue de la carte pour inclure tous les marqueurs (si pas de position utilisateur)
    if (markers.length > 0 && !userLocation) {
        map.fitBounds(bounds);
    }

    // Appliquer les filtres initiaux
    updateMarkersBasedOnFilters();
}

// Fonction pour gérer la géolocalisation
function setupGeolocation() {
    document.getElementById('geolocate-me').addEventListener('click', function() {
        geoloc.getUserLocation(
            // Callback en cas de succès
            (coords) => {
                userLocation = { lat: coords.latitude, lon: coords.longitude };
                activeFilters.proximity = true;
                createUserMarker();
                updateMarkersBasedOnFilters();

                // Mettre à jour l'URL
                const url = new URL(window.location);
                url.searchParams.set('latitude', userLocation.lat);
                url.searchParams.set('longitude', userLocation.lon);
                window.history.pushState({}, '', url);

                // Optionnel : Envoyer au serveur si nécessaire
                geoloc.sendToServer(userLocation.lat, userLocation.lon, (data) => {
                    console.log('Établissements proches :', data.etablissements);
                    // Mettre à jour les données des établissements si besoin
                    const etablissementsDataElement = document.getElementById('etablissements-data');
                    etablissementsDataElement.setAttribute('data-etablissements', JSON.stringify(data.etablissements));
                    updateMapAndMarkers();
                });
            },
            // Callback en cas d'erreur
            (error) => {
                let message = "Erreur de géolocalisation: ";
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        message += "L'utilisateur a refusé la demande de géolocalisation.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message += "Les informations de position sont indisponibles.";
                        break;
                    case error.TIMEOUT:
                        message += "La demande de position a expiré.";
                        break;
                    default:
                        message += error.message;
                }
                alert(message);
            }
        );
    });

    // Gestion du rayon de proximité
    document.getElementById('proximity-radius').addEventListener('change', function() {
        proximityRadius = parseInt(this.value);
 
        updateMarkersBasedOnFilters();
    });
}




//FILTRES


// Fonction pour mettre à jour l'état des boutons actifs
function updateActiveButtonStates() {
    // Désactiver tous les boutons de pâte
    document.querySelectorAll('[id^="filter-type_pate_"]').forEach(button => {
        button.classList.remove('active');
    });
    // Activer le bouton de pâte correspondant si un filtre est actif
    if (activeFilters.type_pate) {
        const pateButton = document.getElementById(`filter-type_pate_${activeFilters.type_pate.toUpperCase()}`);
        if (pateButton) pateButton.classList.add('active');
    }

    // Désactiver tous les boutons de statut
    document.querySelectorAll('[id^="filter-"]:not([id^="filter-type_pate_"]):not([id="filter-all"]):not([id="filter-pate-btn"]):not([id="filter-statut-btn"]):not([id="geolocate-me"])').forEach(button => {
        button.classList.remove('active');
    });
    // Activer les boutons de statut correspondants
    if (activeFilters.visited) document.getElementById('filter-visited').classList.add('active');
    if (activeFilters.unvisited) document.getElementById('filter-unvisited').classList.add('active');
    if (activeFilters.label) document.getElementById('filter-label').classList.add('active');
}

// Fonction utilitaire pour basculer l'état actif d'un bouton
function toggleActiveButton(button, isActive) {
    if (isActive) {
        button.classList.remove('active');
    } else {
        button.classList.add('active');
    }
}

// Fonction pour configurer les boutons de pâte
function setupPateButtons() {
    const pateButtons = {
        'Feuilletée': 'filter-type_pate_FEUILLETEE',
        'Brisée': 'filter-type_pate_BRISEE',
        'Sucrée': 'filter-type_pate_SUCREE',
        'Sablée': 'filter-type_pate_SABLEE',
        'Mixte': 'filter-type_pate_MIXTE'
    };

    Object.entries(pateButtons).forEach(([pateType, buttonId]) => {
        document.getElementById(buttonId).addEventListener('click', function() {
            const isActive = activeFilters.type_pate === pateType;
            activeFilters.type_pate = isActive ? false : pateType;
            activeFilters.visited = false;
            activeFilters.unvisited = false;
            activeFilters.label = false;
            updateMarkersBasedOnFilters();
            updateActiveButtonStates();
            toggleActiveButton(this, isActive);
        });
    });
}

// Fonction pour configurer les boutons de statut
function setupStatutButtons() {
    const statutButtons = {
        'visited': 'filter-visited',
        'unvisited': 'filter-unvisited',
        'label': 'filter-label'
    };

    Object.entries(statutButtons).forEach(([statutType, buttonId]) => {
        document.getElementById(buttonId).addEventListener('click', function() {
            const isActive = activeFilters[statutType];
            activeFilters[statutType] = !isActive;

            // Désactiver les autres filtres de statut si nécessaire
            if (!isActive) {
                Object.keys(statutButtons).filter(key => key !== statutType)
                    .forEach(key => activeFilters[key] = false);
            }
            activeFilters.type_pate = false;

            updateMarkersBasedOnFilters();
            updateActiveButtonStates();
            toggleActiveButton(this, isActive);
        });
    });
}

// Fonction pour configurer les boutons de filtre
function setupFilterButtons() {
    // Ajouter la classe filter-btn à tous les boutons de filtre
    const filterButtons = document.querySelectorAll('#filter-controls button');
    filterButtons.forEach(button => {
        button.classList.add('filter-btn');
    });

    document.getElementById('filter-all').addEventListener('click', function() {
        activeFilters = { type_pate: false, visited: false, unvisited: false, label: false, proximity: false };
        updateMarkersBasedOnFilters();
        document.getElementById('sub-filters').classList.remove('show');
        updateActiveButtonStates();
    });

    // Bouton pour afficher/masquer les options de pâte
    document.getElementById('filter-pate-btn').addEventListener('click', function() {
        const subFilters = document.getElementById('sub-filters');
        if (subFilters.classList.contains('show') && subFilters.querySelector('.filter-group')) {
            subFilters.classList.remove('show');
        } else {
            subFilters.innerHTML = `
                <div class="filter-group">
                    <button id="filter-type_pate_FEUILLETEE" class="btn btn-success">Feuilletée</button>
                    <button id="filter-type_pate_BRISEE" class="btn btn-success">Brisée</button>
                    <button id="filter-type_pate_SUCREE" class="btn btn-success">Sucrée</button>
                    <button id="filter-type_pate_SABLEE" class="btn btn-success">Sablée</button>
                    <button id="filter-type_pate_MIXTE" class="btn btn-success">Mixte</button>
                </div>
            `;
            subFilters.classList.add('show');
            setupPateButtons();
        }
    });

    // Bouton pour afficher/masquer les options de statut
    document.getElementById('filter-statut-btn').addEventListener('click', function() {
        const subFilters = document.getElementById('sub-filters');
        if (subFilters.classList.contains('show') && subFilters.querySelector('.filter-group')) {
            subFilters.classList.remove('show');
        } else {
            subFilters.innerHTML = `
                <div class="filter-group">
                    <button id="filter-visited" class="btn btn-success">Visité</button>
                    <button id="filter-unvisited" class="btn btn-success">Non visité</button>
                    <button id="filter-label" class="btn btn-success">Labellisé</button>
                </div>
            `;
            subFilters.classList.add('show');
            setupStatutButtons();
        }
    });

    document.addEventListener('click', function(event) {
        const subFilters = document.getElementById('sub-filters');
        const filterPateBtn = document.getElementById('filter-pate-btn');
        const filterStatutBtn = document.getElementById('filter-statut-btn');

        // Si le clic n'est pas sur un bouton de filtre ou dans les sous-filtres, on masque les sous-filtres
        if (!filterPateBtn.contains(event.target) &&
            !filterStatutBtn.contains(event.target) &&
            !subFilters.contains(event.target)) {
            subFilters.classList.remove('show');
        }
    });
}

// Initialisation globale
function initAll() {
    initDataElements();
    initMap();
    updateMapAndMarkers();
    setupFilterButtons();
    setupGeolocation();
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', initAll);

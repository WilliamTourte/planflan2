// Variables globales

let map;
let markers = [];
let etablissements = [];
let baseUrl = window.location.origin;

// Variables pour les filtres
let activeFilters = {
    type_pate: false,
    visited: false,
    unvisited: false,
    label: false
};

// Fonction pour initialiser les données dynamiques
function initDataElements() {
    // Vérifier si les éléments de données existent déjà
    if (!document.getElementById('etablissements-data')) {
        // Créer l'élément pour les données des établissements
        const etablissementsDataElement = document.createElement('div');
        etablissementsDataElement.id = 'etablissements-data';
        etablissementsDataElement.setAttribute('data-etablissements', '[]');
        document.body.appendChild(etablissementsDataElement);
    }
    
    if (!document.getElementById('is-admin')) {
        // Créer l'élément pour l'état admin
        const isAdminElement = document.createElement('div');
        isAdminElement.id = 'is-admin';
        isAdminElement.setAttribute('data-is-admin', 'false');
        document.body.appendChild(isAdminElement);
    }
    
    if (!document.getElementById('google-maps-api-key')) {
        // Créer l'élément pour la clé API Google Maps
        const googleMapsApiKeyElement = document.createElement('div');
        googleMapsApiKeyElement.id = 'google-maps-api-key';
        googleMapsApiKeyElement.setAttribute('data-api-key', '');
        document.body.appendChild(googleMapsApiKeyElement);
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

function closeInfoWindow() {
    // Leaflet gère la fermeture des popups automatiquement
}

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
    document.querySelectorAll('[id^="filter-"]:not([id^="filter-type_pate_"]):not([id="filter-all"]):not([id="filter-pate-btn"]):not([id="filter-statut-btn"])').forEach(button => {
        button.classList.remove('active');
    });
    // Activer les boutons de statut correspondants
    if (activeFilters.visited) document.getElementById('filter-visited').classList.add('active');
    if (activeFilters.unvisited) document.getElementById('filter-unvisited').classList.add('active');
    if (activeFilters.label) document.getElementById('filter-label').classList.add('active');
}


// Fonction pour mettre à jour l'affichage des marqueurs en fonction des filtres
function updateMarkersBasedOnFilters() {
    markers.forEach(marker => {
        const etablissement = marker.options.etablissement;
        let showMarker = true;

        // Vérifier si l'établissement a au moins un flan correspondant au filtre de type de pâte
        if (activeFilters.type_pate) {
            if (!etablissement.flans || etablissement.flans.length === 0) {
                showMarker = false;
            } else {
                const hasMatchingPate = etablissement.flans.some(flan => flan.type_pate === activeFilters.type_pate);
                if (!hasMatchingPate) {
                    showMarker = false;
                }
            }
        }

        // Vérifier les autres filtres
        if (activeFilters.visited && !etablissement.visite) {
            showMarker = false;
        }
        if (activeFilters.unvisited && etablissement.visite) {
            showMarker = false;
        }
        if (activeFilters.label && !etablissement.label) {
            showMarker = false;
        }

        if (showMarker) {
            map.addLayer(marker);
        } else {
            map.removeLayer(marker);
        }
    });
}

// Initialisation de la carte Leaflet
function initMap() {
    console.log("Initialisation de la carte...");
    const mapElement = document.getElementById("map");
    if (!mapElement) {
        console.error("Élément #map introuvable !");
        return;
    }
    map = L.map('map').setView([46.2276, 2.2137], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    console.log("Carte initialisée avec succès.");
}


// Chargement des établissements depuis les données intégrées
function loadEtablissements() {
    try {
        const etablissementsDataElement = document.getElementById('etablissements-data');
        if (!etablissementsDataElement) {
            console.error("Élément #etablissements-data introuvable !");
            return [];
        }
        const etablissementsData = JSON.parse(etablissementsDataElement.getAttribute('data-etablissements'));
        return etablissementsData;
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
    let icon = createEmojiIcon('🏠', 'default-icon');
    if (etablissement.label) icon = createEmojiIcon('❤️', 'label-icon');
    else if (etablissement.visite) icon = createEmojiIcon('✅', 'visited-icon');
    else icon = createEmojiIcon('👋', 'unvisited-icon');

    if (etablissement.latitude && etablissement.longitude) {
        const marker = L.marker(
            [etablissement.latitude, etablissement.longitude],
            { icon: icon, title: etablissement.nom }
        ).addTo(map);

        // Chargement asynchrone de l'infowindow (sans ouverture automatique)
        marker.bindPopup("Chargement en cours...");
        fetch(`/get_infowindow_content?id_etab=${etablissement.id_etab}`)
            .then(response => response.text())
            .then(content => {
                marker.setPopupContent(content);
            })
            .catch(error => {
                console.error('Erreur lors du chargement de l\'infowindow:', error);
                let popupContent = `<div class="infowindow-content"><h4>${etablissement.nom}</h4>`;
                popupContent += `<p>${etablissement.adresse}, ${etablissement.ville}</p>`;
                popupContent += `<a href="${baseUrl}/etablissement/${etablissement.id_etab}" class="btn btn-sm btn-success">Voir plus</a></div>`;
                marker.setPopupContent(popupContent);
            });

        marker.options.etablissement = etablissement;
        markers.push(marker);
        bounds.extend(marker.getLatLng());
    }
});

    // Ajuste la vue
    if (etablissements.length > 0) {
        map.fitBounds(bounds);
    }

    // Appliquer les filtres initiaux
    updateMarkersBasedOnFilters();
}


// Fonction pour gérer les clics sur les boutons de filtre
function setupFilterButtons() {
    // Ajouter la classe filter-btn à tous les boutons de filtre
    const filterButtons = document.querySelectorAll('#filter-controls button');
    filterButtons.forEach(button => {
        button.classList.add('filter-btn');
    });
    
    document.getElementById('filter-all').addEventListener('click', function() {
        activeFilters = { type_pate: false, visited: false, unvisited: false, label: false };
        updateMarkersBasedOnFilters();
        document.getElementById('sub-filters').classList.remove('show');
        updateActiveButtonStates();
    });
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
    console.log("Initialisation de l'application...");
    initDataElements(); // Initialiser les éléments de données
    initMap();
    updateMapAndMarkers();
    setupFilterButtons(); // Initialiser les boutons de filtre
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM chargé.");
    const googleMapsApiKey = document.getElementById('google-maps-api-key')?.getAttribute('data-api-key');
    if (!googleMapsApiKey) {
        console.error("Clé API Google Maps introuvable !");
        return;
    }
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&libraries=places&callback=initAll&v=weekly`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
});

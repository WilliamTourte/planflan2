// Variables globales
let map;
let markers = [];
let etablissements = [];
let userMarker = null;

let baseUrl = window.location.origin;
let userLocation = null;
let proximityRadius = 5;
let villeSelectionnee = null;

// Variables pour les filtres
let activeFilters = {
    type_pate: false,
    type_saveur: false,
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
  
    }

    // Récupérer la ville sélectionnée si disponible
    const villeSelectionneeElement = document.getElementById('ville-selectionnee');
    if (villeSelectionneeElement) {
        villeSelectionnee = villeSelectionneeElement.getAttribute('data-ville');
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


        // Filtre par type de pâte (logique ET cumulative)
        if (activeFilters.type_pate) {
            if (!etablissement.flans || etablissement.flans.length === 0) {
                showMarker = false;
            } else {
                const hasMatchingPate = etablissement.flans.some(flan => flan.type_pate === activeFilters.type_pate);
                showMarker = showMarker && hasMatchingPate;
            }
        }

        // Filtre par type de saveur (logique ET cumulative)
        if (activeFilters.type_saveur) {
            if (!etablissement.flans || etablissement.flans.length === 0) {
                showMarker = false;
            } else {
                const hasMatchingSaveur = etablissement.flans.some(flan => flan.type_saveur === activeFilters.type_saveur);
                showMarker = showMarker && hasMatchingSaveur;
            }
        }

        // Filtres de statut (logique ET cumulative)
        if (activeFilters.visited) showMarker = showMarker && etablissement.visite;
        if (activeFilters.unvisited) showMarker = showMarker && !etablissement.visite;
        if (activeFilters.label) showMarker = showMarker && etablissement.label;

        if (showMarker) {
            map.addLayer(marker);
        } else {
            map.removeLayer(marker);
        }
    });
}

// Fonction pour zoomer sur une ville spécifique
function zoomOnVille(ville) {
    if (!ville || !etablissements || etablissements.length === 0) {
        return false;
    }

    // Trouver les établissements de cette ville
    const etablissementsVille = etablissements.filter(etab => 
        etab.ville && etab.ville.toLowerCase().includes(ville.toLowerCase())
    );

    if (etablissementsVille.length === 0) {
        return false;
    }

    // Créer un groupe de coordonnées pour ces établissements
    const villeBounds = L.latLngBounds();
    etablissementsVille.forEach(etab => {
        if (etab.latitude && etab.longitude) {
            villeBounds.extend([etab.latitude, etab.longitude]);
        }
    });

    if (villeBounds.isValid()) {
        // Zoomer sur les établissements de cette ville
        map.fitBounds(villeBounds);
        return true;
    }

    return false;
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
// Fonction pour ajouter le bouton de géolocalisation comme contrôle Leaflet
function addGeolocateControl() {
    const geolocateControl = L.control({ position: 'bottomright' });

    geolocateControl.onAdd = function(map) {
        // Créer le conteneur avec les classes CSS
        const container = L.DomUtil.create('div', 'leaflet-control-geolocate geolocate-button');
        L.DomUtil.addClass(container, 'leaflet-bar leaflet-control');

        const link = L.DomUtil.create('a', '', container);
        link.href = '#';
        link.title = 'Géolocalisation';

        // Créer l'icône de géolocalisation
        const icon = L.DomUtil.create('i', 'bi bi-geo-alt-fill', link);

        // Gérer le clic sur le bouton
        L.DomEvent.on(link, 'click', L.DomEvent.stopPropagation)
            .on(link, 'click', L.DomEvent.preventDefault)
            .on(link, 'click', function() {
                geoloc.getUserLocation(
                    (coords) => {
                        userLocation = { lat: coords.latitude, lon: coords.longitude };
                        activeFilters.proximity = true;
                        createUserMarker();

                        // Met à jour les champs cachés du formulaire (si ils existent)
                        const latitudeInput = document.getElementById('latitude');
                        const longitudeInput = document.getElementById('longitude');

                        if (latitudeInput && longitudeInput) {
                            latitudeInput.value = coords.latitude;
                            longitudeInput.value = coords.longitude;

                            // Soumet le formulaire seulement si les champs de coordonnées existent
                            const form = document.querySelector('form');
                            if (form) {
                                form.submit();
                            }
                        } else {
                            // Si les champs n'existent pas, on recrée juste la carte avec la nouvelle position
                            createUserMarker();
                            updateMarkersBasedOnFilters();
                        }
                    },
                    (error) => {
                        // Gestion des erreurs
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

        return container;
    };

    geolocateControl.addTo(map);
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
    
    // Ajouter un écouteur d'événement pour le déplacement de la carte
    map.on('moveend', function() {
        // Sauvegarder l'état dans l'URL lorsque la carte est déplacée
        saveStateToUrl();
    });

    // Ajouter le bouton de géolocalisation comme contrôle Leaflet
    addGeolocateControl();

    // Légende
    const legend = L.control({ position: 'bottomleft' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'carte-legende');

div.innerHTML = `
    <div class="legende-container">
        <div class="legende-item">
            ❤️
            <span class="legende-text">Labellisé</span>
        </div>
        <div class="legende-item">
            ✅
            <span class="legende-text">Visité</span>
        </div>
        <div class="legende-item">
            👋
            <span class="legende-text">Non visité</span>
        </div>
    </div>
`;

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
        // Si une ville est sélectionnée, zoomer dessus
        if (villeSelectionnee && zoomOnVille(villeSelectionnee)) {
            console.log(`Zoom sur la ville: ${villeSelectionnee}`);
        } else {
            // Sinon, afficher tous les établissements
            map.fitBounds(bounds);
        }
    }

    // Appliquer les filtres initiaux
    updateMarkersBasedOnFilters();
}

// Fonction pour gérer la géolocalisation - zoom seulement, sans filtrage
function setupGeolocation() {
    const geolocateButton = document.getElementById('geolocate-me');
    if (geolocateButton) {
        geolocateButton.addEventListener('click', function() {
            geoloc.getUserLocation(
                (coords) => {
                    userLocation = { lat: coords.latitude, lon: coords.longitude };
                    
                    // Créer le marqueur utilisateur
                    createUserMarker();
                    
                    // Zoomer sur la position utilisateur (sans filtrer les établissements)
                    if (map) {
                        map.setView([coords.latitude, coords.longitude], 15);
                    }
                },
                (error) => {
                    // Gestion des erreurs
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
    }
}



//FILTRES


// Fonction pour mettre à jour l'état des boutons actifs
function updateActiveButtonStates() {
    // Gérer les boutons de pâte
    document.querySelectorAll('[id^="filter-type_pate_"]').forEach(button => {
        const pateType = button.textContent.trim();
        if (activeFilters.type_pate === pateType) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // Gérer les boutons de saveur
    document.querySelectorAll('[id^="filter-type_saveur_"]').forEach(button => {
        const saveurType = button.textContent.trim();
        if (activeFilters.type_saveur === saveurType) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // Gérer les boutons de statut
    document.querySelectorAll('[id^="filter-"]:not([id^="filter-type_pate_"]):not([id^="filter-type_saveur_"]):not([id="filter-all"]):not([id="filter-pate-btn"]):not([id="filter-saveur-btn"]):not([id="filter-statut-btn"]):not([id="geolocate-me"])').forEach(button => {
        const buttonId = button.id;
        if (buttonId === 'filter-visited' && activeFilters.visited) {
            button.classList.add('active');
        } else if (buttonId === 'filter-unvisited' && activeFilters.unvisited) {
            button.classList.add('active');
        } else if (buttonId === 'filter-label' && activeFilters.label) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// Fonction utilitaire pour basculer l'état actif d'un bouton
function toggleActiveButton(button, isActive) {
    if (isActive) {
        button.classList.remove('active');
    } else {
        button.classList.add('active');
    }
}

// Fonction pour mettre à jour la couleur des boutons principaux
function updateMainFilterButtons() {
    // Réinitialiser tous les boutons principaux
    document.getElementById('filter-pate-btn').classList.remove('active');
    document.getElementById('filter-saveur-btn').classList.remove('active');
    document.getElementById('filter-statut-btn').classList.remove('active');

    // Mettre en bleu les boutons dont la catégorie a des filtres actifs
    if (activeFilters.type_pate) {
        document.getElementById('filter-pate-btn').classList.add('active');
    }
    if (activeFilters.type_saveur) {
        document.getElementById('filter-saveur-btn').classList.add('active');
    }
    if (activeFilters.visited || activeFilters.unvisited || activeFilters.label) {
        document.getElementById('filter-statut-btn').classList.add('active');
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
            // Ne plus désactiver les autres filtres - permettre la combinaison
            updateMarkersBasedOnFilters();
            updateActiveButtonStates();
            updateMainFilterButtons();
            toggleActiveButton(this, isActive);
            
            // Sauvegarder l'état dans l'URL
            saveStateToUrl();
        });
    });
}

// Fonction pour configurer les boutons de saveur
function setupSaveurButtons() {
    const saveurButtons = {
        'Vanille': 'filter-type_saveur_VANILLE',
        'Chocolat': 'filter-type_saveur_CHOCOLAT',
        'Noix': 'filter-type_saveur_NOIX',
        'Fruits': 'filter-type_saveur_FRUITS',
        'Insolite': 'filter-type_saveur_INSOLITE',
        'Nature': 'filter-type_saveur_NATURE'
    };

    Object.entries(saveurButtons).forEach(([saveurType, buttonId]) => {
        document.getElementById(buttonId).addEventListener('click', function() {
            const isActive = activeFilters.type_saveur === saveurType;
            activeFilters.type_saveur = isActive ? false : saveurType;
            // Ne plus désactiver les autres filtres - permettre la combinaison
            updateMarkersBasedOnFilters();
            updateActiveButtonStates();
            updateMainFilterButtons();
            toggleActiveButton(this, isActive);
            
            // Sauvegarder l'état dans l'URL
            saveStateToUrl();
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
            // Ne plus désactiver les filtres de pâte/saveur - permettre la combinaison

            updateMarkersBasedOnFilters();
            updateActiveButtonStates();
            updateMainFilterButtons();
            toggleActiveButton(this, isActive);
            
            // Sauvegarder l'état dans l'URL
            saveStateToUrl();
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
        activeFilters = { type_pate: false, type_saveur: false, visited: false, unvisited: false, label: false, proximity: false };
        updateMarkersBasedOnFilters();
        document.getElementById('sub-filters').classList.remove('show');
        updateActiveButtonStates();
        updateMainFilterButtons();
        
        // Sauvegarder l'état dans l'URL
        saveStateToUrl();
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
            updateActiveButtonStates(); // ← Restaurer les états actifs
            updateMainFilterButtons(); // ← Mettre à jour les boutons principaux
        }
    });

    // Bouton pour afficher/masquer les options de saveur
    document.getElementById('filter-saveur-btn').addEventListener('click', function() {
        const subFilters = document.getElementById('sub-filters');
        if (subFilters.classList.contains('show') && subFilters.querySelector('.filter-group')) {
            subFilters.classList.remove('show');
        } else {
            subFilters.innerHTML = `
                <div class="filter-group">
                    <button id="filter-type_saveur_VANILLE" class="btn btn-success">Vanille</button>
                    <button id="filter-type_saveur_CHOCOLAT" class="btn btn-success">Chocolat</button>
                    <button id="filter-type_saveur_NOIX" class="btn btn-success">Noix</button>
                    <button id="filter-type_saveur_FRUITS" class="btn btn-success">Fruits</button>
                    <button id="filter-type_saveur_INSOLITE" class="btn btn-success">Insolite</button>
                    <button id="filter-type_saveur_NATURE" class="btn btn-success">Nature</button>
                </div>
            `;
            subFilters.classList.add('show');
            setupSaveurButtons();
            updateActiveButtonStates(); // ← Restaurer les états actifs
            updateMainFilterButtons(); // ← Mettre à jour les boutons principaux
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
            updateActiveButtonStates(); // ← Restaurer les états actifs
            updateMainFilterButtons(); // ← Mettre à jour les boutons principaux
        }
    });

    document.addEventListener('click', function(event) {
        const subFilters = document.getElementById('sub-filters');
        const filterPateBtn = document.getElementById('filter-pate-btn');
        const filterSaveurBtn = document.getElementById('filter-saveur-btn');
        const filterStatutBtn = document.getElementById('filter-statut-btn');

        // Si le clic n'est pas sur un bouton de filtre ou dans les sous-filtres, on masque les sous-filtres
        if (!filterPateBtn.contains(event.target) &&
            !filterSaveurBtn.contains(event.target) &&
            !filterStatutBtn.contains(event.target) &&
            !subFilters.contains(event.target)) {
            subFilters.classList.remove('show');
        }
    });
}

// Fonction pour sauvegarder l'état dans l'URL
function saveStateToUrl() {
    const url = new URL(window.location.href);
    
    // Sauvegarder les filtres
    if (activeFilters.type_pate) {
        url.searchParams.set('pate', activeFilters.type_pate);
    } else {
        url.searchParams.delete('pate');
    }
    
    if (activeFilters.type_saveur) {
        url.searchParams.set('saveur', activeFilters.type_saveur);
    } else {
        url.searchParams.delete('saveur');
    }
    
    if (activeFilters.visited) {
        url.searchParams.set('visited', 'true');
    } else {
        url.searchParams.delete('visited');
    }
    
    if (activeFilters.unvisited) {
        url.searchParams.set('unvisited', 'true');
    } else {
        url.searchParams.delete('unvisited');
    }
    
    if (activeFilters.label) {
        url.searchParams.set('label', 'true');
    } else {
        url.searchParams.delete('label');
    }
    
    // Sauvegarder la position et le zoom de la carte
    if (map) {
        const center = map.getCenter();
        url.searchParams.set('lat', center.lat.toFixed(6));
        url.searchParams.set('lng', center.lng.toFixed(6));
        url.searchParams.set('zoom', map.getZoom());
    }
    
    window.history.replaceState({}, '', url);
}

// Fonction pour restaurer l'état depuis l'URL
function restoreStateFromUrl() {
    const url = new URL(window.location.href);
    
    // Restaurer les filtres
    if (url.searchParams.has('pate')) {
        activeFilters.type_pate = url.searchParams.get('pate');
    }
    
    if (url.searchParams.has('saveur')) {
        activeFilters.type_saveur = url.searchParams.get('saveur');
    }
    
    if (url.searchParams.has('visited')) {
        activeFilters.visited = url.searchParams.get('visited') === 'true';
    }
    
    if (url.searchParams.has('unvisited')) {
        activeFilters.unvisited = url.searchParams.get('unvisited') === 'true';
    }
    
    if (url.searchParams.has('label')) {
        activeFilters.label = url.searchParams.get('label') === 'true';
    }
    
    // Restaurer la position et le zoom de la carte
    if (map && url.searchParams.has('lat') && url.searchParams.has('lng') && url.searchParams.has('zoom')) {
        const lat = parseFloat(url.searchParams.get('lat'));
        const lng = parseFloat(url.searchParams.get('lng'));
        const zoom = parseInt(url.searchParams.get('zoom'));
        
        if (!isNaN(lat) && !isNaN(lng) && !isNaN(zoom)) {
            map.setView([lat, lng], zoom);
        }
    }
}

// Initialisation globale
function initAll() {
    initDataElements();
    initMap();
    updateMapAndMarkers();
    setupFilterButtons();
    setupGeolocation();
    
    // Restaurer l'état depuis l'URL
    restoreStateFromUrl();
    
    // Mettre à jour les boutons pour refléter l'état restauré
    updateActiveButtonStates();
    updateMainFilterButtons();
    
    // Sauvegarder l'état initial
    saveStateToUrl();
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', initAll);

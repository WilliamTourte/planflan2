/**
 * Module de gestion de la carte pour l'application PlanFlan
 * 
 * Ce module gère l'initialisation et les interactions avec la carte Leaflet
 */

import { GeolocationHandler } from './geolocation.js';

// Variables globales pour le module
let map;
let markers = [];
let etablissements = [];
let userMarker = null;
let geolocationHandler = null;
let baseUrl = window.location.origin;
let userLocation = null;
let villeSelectionnee = null;

// État des filtres actifs pour la carte
let activeFilters = {
    type_pate: false,
    type_saveur: false,
    visited: false,
    unvisited: false,
    label: false
};

/**
 * Fonction pour créer des icônes personnalisées
 * @param {string} emoji - Emoji à utiliser
 * @param {string} className - Classe CSS supplémentaire
 * @returns {object} Icône Leaflet personnalisée
 */
export function createEmojiIcon(emoji, className) {
    return L.divIcon({
        html: `<div class="emoji-marker ${className}">${emoji}</div>`,
        className: 'emoji-icon',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
}

/**
 * Crée un marqueur avec un popup asynchrone pour un établissement donné.
 * @param {object} map - Instance de la carte Leaflet
 * @param {object} etablissement - Données de l'établissement
 * @param {string} context - Contexte ('existing' ou 'proposition')
 * @param {string} baseUrl - URL de base pour les liens (par défaut: origine du site)
 * @returns {object} Marqueur Leaflet créé
 */
export function createInfowindowMarker(map, etablissement, context = 'existing', baseUrl = window.location.origin) {
    console.log('createInfowindowMarker appelé avec:', {
        mapExists: !!map,
        mapType: typeof map,
        hasAddLayer: !!map?.addLayer,
        addLayerIsFunction: typeof map?.addLayer === 'function',
        mapObject: map,
        etablissement: etablissement
    });
    
    // Validation de la carte
    if (!map || !map.addLayer || typeof map.addLayer !== 'function') {
        console.error('createInfowindowMarker: map parameter is not a valid Leaflet map object', map);
        throw new Error('Invalid map object provided to createInfowindowMarker');
    }
    
    // Validation supplémentaire: vérifier que la carte est bien une instance Leaflet
    try {
        // Tester quelques propriétés et méthodes essentielles
        const isValidLeafletMap = 
            typeof map.getCenter === 'function' &&
            typeof map.setView === 'function' &&
            typeof map.removeLayer === 'function' &&
            typeof map.addLayer === 'function';
        
        if (!isValidLeafletMap) {
            console.error('createInfowindowMarker: map object is not a valid Leaflet map instance', {
                hasGetCenter: typeof map.getCenter === 'function',
                hasSetView: typeof map.setView === 'function',
                hasRemoveLayer: typeof map.removeLayer === 'function',
                hasAddLayer: typeof map.addLayer === 'function'
            });
            throw new Error('Invalid Leaflet map instance provided to createInfowindowMarker');
        }
    } catch (e) {
        console.error('createInfowindowMarker: error validating map instance', e);
        throw new Error('Error validating map instance in createInfowindowMarker');
    }

    // Déterminer l'icône en fonction du contexte
    let icon;
    if (context === 'existing') {
        if (etablissement.label) {
            icon = createEmojiIcon('❤️', 'label-icon');
        } else if (etablissement.visite) {
            icon = createEmojiIcon('✅', 'visited-icon');
        } else {
            icon = createEmojiIcon('👋', 'unvisited-icon');
        }
    } else {
        icon = createEmojiIcon('🏠', 'proposition-icon');
    }

    const marker = L.marker(
        [etablissement.latitude, etablissement.longitude],
        { icon: icon, title: etablissement.nom }
    ).addTo(map);

    // Ne pas charger le popup immédiatement, mais seulement au clic
    marker.on('click', function() {
        // Vérifier si le popup existe et est ouvert
        if (marker.getPopup() && marker._popup.isOpen()) {
            // Le popup est déjà ouvert, ne rien faire
            return;
        }

        // Si le popup existe mais est fermé, le supprimer
        if (marker.getPopup()) {
            marker.unbindPopup();
        }

        // Créer un nouveau popup
        const popup = L.popup({
            autoPan: true,
            autoPanPadding: [50, 50], // Marge pour éviter que le popup soit collé aux bords
            keepInView: true,
            closeButton: true,
        });

        const popupContainer = L.DomUtil.create('div', 'custom-popup-container');
        
        // Ajouter un bouton de fermeture personnalisé pour s'assurer qu'il est visible
        const closeButton = L.DomUtil.create('button', 'custom-close-button', popupContainer);
        closeButton.innerHTML = '×';
        closeButton.style.position = 'absolute';
        closeButton.style.top = '5px';
        closeButton.style.right = '25px';
        closeButton.style.zIndex = '1000';
        closeButton.style.fontSize = '20px';
        closeButton.style.background = 'none';
        closeButton.style.border = 'none';
        closeButton.style.cursor = 'pointer';
        closeButton.style.padding = '0';
        closeButton.style.width = '25px';
        closeButton.style.height = '25px';
        
        closeButton.onclick = function(e) {
            e.stopPropagation();
            map.closePopup(popup);
        };
        popup.setContent(popupContainer);
        marker.bindPopup(popup).openPopup();

        setTimeout(() => {
            map.panTo(marker.getLatLng());
        }, 100);

        // Construction de l'URL en fonction du contexte
        let url;
        if (context === 'existing') {
            url = `/get_infowindow_content?id_etab=${etablissement.id_etab}&context=existing`;
        } else {
            url = `/get_infowindow_content?context=proposition&` +
                 `nom=${encodeURIComponent(etablissement.nom)}&` +
                 `adresse=${encodeURIComponent(etablissement.adresse)}&` +
                 `ville=${encodeURIComponent(etablissement.ville)}&` +
                 `type_etab=${etablissement.type_etab}`;
        }

        fetch(url)
            .then(response => response.text())
            .then(content => {
                popupContainer.innerHTML = content;
                marker._popup.update();
                // Forcer le recalcul de position après chargement du contenu
                setTimeout(() => {
                    if (marker._popup) {
                        marker._popup.update();
                        map.panTo(marker.getLatLng());
                    }
                }, 50);
            })
            .catch(error => {
                console.error('Erreur lors du chargement du popup:', error);
                let popupContent = `<div class="infowindow-content"><h4>${etablissement.nom}</h4>`;
                popupContent += `<p>${etablissement.adresse}, ${etablissement.ville}</p>`;
                if (context === 'existing') {
                    popupContent += `<a href="${baseUrl}/etablissement/${etablissement.id_etab}" class="btn btn-success">Voir plus</a>`;
                }
                popupContent += `</div>`;
                popupContainer.innerHTML = popupContent;
                marker._popup.update();
                // Forcer le recalcul de position même en cas d'erreur
                setTimeout(() => {
                    if (marker._popup) {
                        marker._popup.update();
                        map.panTo(marker.getLatLng());
                    }
                }, 50);
            });
    });

    marker.options.etablissement = etablissement;
    return marker;
}

// Conserver l'ancienne fonction pour la compatibilité
export function createEtablissementMarker(map, etablissement, baseUrl) {
    return createInfowindowMarker(map, etablissement, 'existing', baseUrl);
}

/**
 * Zoom sur une ville spécifique et centre la carte sur ses établissements.
 * @param {string} ville - Nom de la ville sur laquelle zoomer
 * @returns {boolean} True si le zoom a été effectué, false sinon
 */
export function zoomOnVille(ville) {
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

/**
 * Crée un marqueur pour la position de l'utilisateur.
 * @param {boolean} forceZoom - Si true, zoom sur la position de l'utilisateur
 */
export function createUserMarker(forceZoom = false) {
    // Supprimer l'ancien marqueur s'il existe
    if (userMarker) {
        map.removeLayer(userMarker);
        userMarker = null;
    }

    if (userLocation && geolocationHandler) {
        // Créer une position mock avec les coordonnées existantes
        const mockPosition = {
            coords: {
                latitude: userLocation.lat,
                longitude: userLocation.lon,
                accuracy: 50 // Précision par défaut pour le cercle
            }
        };

        // Utiliser GeolocationHandler pour créer le marqueur avec cercle de précision
        // Cela garantit un comportement uniforme
        geolocationHandler._handlePosition(mockPosition);

        // Centrer la carte sur l'utilisateur seulement si forceZoom est vrai
        if (forceZoom) {
            map.setView([userLocation.lat, userLocation.lon], 13);
        }
    } else if (userLocation) {
        // Fallback si GeolocationHandler n'est pas disponible
        userMarker = L.marker([userLocation.lat, userLocation.lon], {
            icon: createEmojiIcon('📍', 'localisation-icon')
        }).addTo(map);

        if (forceZoom) {
            map.setView([userLocation.lat, userLocation.lon], 13);
        }
    }
}

/**
 * Ajoute un bouton de géolocalisation à la carte Leaflet
 * @param {object} map - Instance de la carte Leaflet
 * @returns {void}
 */
export function addGeolocateControl(map) {
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
                // Utiliser le nouveau gestionnaire de géolocalisation
                geolocationHandler.activate()
                    .then(() => {
                        // Succès - la carte est déjà centrée par le gestionnaire
                        console.log("Géolocalisation réussie");
                    })
                    .catch(error => {
                        console.error("Erreur de géolocalisation:", error.message);
                    });
            });

        return container;
    };

    geolocateControl.addTo(map);
}

/**
 * Initialise la carte Leaflet avec un marqueur unique pour un établissement.
 * Utilisée sur la page de proposition d'établissement.
 * @param {number} lat - Latitude de l'établissement
 * @param {number} lng - Longitude de l'établissement
 * @param {string} nom - Nom de l'établissement
 * @returns {object} Instance de la carte Leaflet
 */
export function initMapWithMarker(lat, lng, nom) {
    const mapElement = document.getElementById("map");
    if (!mapElement) {
        console.error("Élément #map introuvable !");
        return;
    }

    // Réutiliser la carte si elle existe déjà
    if (map) {
        console.log("Carte existante détectée, réutilisation et nettoyage des marqueurs");
        // Supprimer les marqueurs existants
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });
        // Centrer sur la nouvelle position
        map.setView([lat, lng], 15);
    } else {
        console.log("Création d'une nouvelle carte pour proposer_etablissement");
        // Créer une nouvelle carte
        map = L.map('map').setView([lat, lng], 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
    }

    // Ajouter un marqueur pour l'établissement
    const marker = L.marker([lat, lng])
        .addTo(map)
        .bindPopup(`<b>${nom}</b>`)
        .openPopup();

    console.log(`Marqueur ajouté pour ${nom} à [${lat}, ${lng}]`);

    return map;
}

/**
 * Initialise la carte Leaflet avec les paramètres par défaut.
 * Configure la vue initiale et les contrôles de base.
 * @param {object} options - Options de configuration
 * @returns {void}
 */
export function initMap(options = {}) {
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

    // Initialiser le gestionnaire de géolocalisation
    geolocationHandler = new GeolocationHandler(map, {
        defaultZoom: 14
    });

    // Ajouter un écouteur d'événement pour le déplacement de la carte
    map.on('moveend', function() {
        // Sauvegarder l'état dans l'URL lorsque la carte est déplacée
        saveCompleteStateToUrl();
    });

    // Ajouter le bouton de géolocalisation comme contrôle Leaflet
    addGeolocateControl(map);

    // Légende
    const legend = L.control({ position: 'bottomleft' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'carte-legende');
        
        div.innerHTML = `
            <div class="legende-text">
                ❤️ Labellisé ✅ Visité 👋 Non visité
            </div>
        `;
        
        return div;
    };
    legend.addTo(map);

    return map;
}

/**
 * Charge les données des établissements depuis le DOM
 * @returns {Array} Liste des établissements
 */
export function loadEtablissements() {
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

/**
 * Met à jour la carte et les marqueurs avec les données actuelles
 * @returns {void}
 */
export function updateMapAndMarkers() {
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
        if (villeSelectionnee) {
            if (zoomOnVille(villeSelectionnee)) {
                console.log(`Zoom sur les établissements de la ville: ${villeSelectionnee}`);
            } else if (userLocation) {
                // Si la ville n'a pas d'établissements mais qu'on a des coordonnées, zoomer sur la ville
                console.log(`Zoom sur la ville sans établissements: ${villeSelectionnee}`);
                map.setView([userLocation.lat, userLocation.lon], 13);
            } else {
                // Sinon, afficher tous les établissements
                map.fitBounds(bounds);
            }
        } else {
            // Sinon, afficher tous les établissements
            map.fitBounds(bounds);
        }
    }

    // Appliquer les filtres initiaux
    updateMarkersBasedOnFilters();
}

/**
 * Met à jour les marqueurs en fonction des filtres actifs.
 * Affiche ou masque les marqueurs selon les critères de filtrage sélectionnés.
 */
export function updateMarkersBasedOnFilters() {
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

/**
 * Définit les filtres actifs pour la carte
 * @param {object} newFilters - Nouvel ensemble de filtres
 * @returns {void}
 */
export function setActiveFilters(newFilters) {
    activeFilters = { ...activeFilters, ...newFilters };
}

/**
 * Récupère l'état actuel des filtres
 * @returns {object} Filtres actuels
 */
export function getActiveFilters() {
    return activeFilters;
}

/**
 * Définit la localisation de l'utilisateur
 * @param {object} location - Objet location avec lat et lon
 * @returns {void}
 */
export function setUserLocation(location) {
    userLocation = location;
}

/**
 * Définit la ville sélectionnée
 * @param {string} ville - Nom de la ville
 * @returns {void}
 */
export function setVilleSelectionnee(ville) {
    villeSelectionnee = ville;
}

/**
 * Sauvegarde l'état complet (filtres + carte) dans l'URL
 */
export function saveCompleteStateToUrl() {
    const url = new URL(window.location.href);
    const currentFilters = getActiveFilters();
    
    // Sauvegarder les filtres
    if (currentFilters.type_pate) {
        url.searchParams.set('pate', currentFilters.type_pate);
    } else {
        url.searchParams.delete('pate');
    }
    
    if (currentFilters.type_saveur) {
        url.searchParams.set('saveur', currentFilters.type_saveur);
    } else {
        url.searchParams.delete('saveur');
    }
    
    if (currentFilters.visited) {
        url.searchParams.set('visited', 'true');
    } else {
        url.searchParams.delete('visited');
    }
    
    if (currentFilters.unvisited) {
        url.searchParams.set('unvisited', 'true');
    } else {
        url.searchParams.delete('unvisited');
    }
    
    if (currentFilters.label) {
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

// Export pour compatibilité avec les anciens scripts
document.map = {
    initMap,
    initMapWithMarker,
    createEtablissementMarker,
    zoomOnVille,
    createUserMarker,
    addGeolocateControl,
    updateMapAndMarkers,
    updateMarkersBasedOnFilters,
    setActiveFilters,
    getActiveFilters,
    setUserLocation,
    setVilleSelectionnee,
    loadEtablissements,
    saveCompleteStateToUrl
};
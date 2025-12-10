// Variables globales
let autocomplete;
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

// Initialisation de l'autocomplétion Google Maps
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
        if (!place.geometry) {
            console.error("Aucune géométrie trouvée pour ce lieu.");
            return;
        }
        // Remplir les champs CACHÉS avec le préfixe "ajout-etab-"
        const nomElement = document.getElementById('ajout-etab-nom');
        const adresseElement = document.getElementById('ajout-etab-adresse');
        const latitudeElement = document.getElementById('ajout-etab-latitude');
        const longitudeElement = document.getElementById('ajout-etab-longitude');
        if (nomElement) nomElement.value = place.name || '';
        if (adresseElement) adresseElement.value = place.formatted_address || '';
        if (latitudeElement) latitudeElement.value = place.geometry.location.lat();
        if (longitudeElement) longitudeElement.value = place.geometry.location.lng();
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
                const formContainer = document.querySelector('.form-container');
                if (formContainer) formContainer.prepend(message);
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
        });
    });
};

// Chargement des établissements depuis les données intégrées
function loadEtablissements() {
    try {
        const etablissementsDataElement = document.getElementById('etablissements-data');
        if (!etablissementsDataElement) {
            console.error("Élément #etablissements-data introuvable !");
            return [];
        }
        const etablissementsData = JSON.parse(etablissementsDataElement.getAttribute('data-etablissements'));
        console.log("Données des établissements chargées:", etablissementsData);
        etablissementsData.forEach(etab => {
            console.log(`Établissement: ${etab.nom}, Flans:`, etab.flans);
            if (etab.flans && etab.flans.length > 0) {
                etab.flans.forEach(flan => {
                    console.log(`Flan: ${flan.nom}, type_pate: ${flan.type_pate}`);
                });
            }
        });
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
        console.log(`Établissement: ${etablissement.nom}, Lat: ${etablissement.latitude}, Lng: ${etablissement.longitude}`);
        let icon = createEmojiIcon('🏠', 'default-icon');
        if (etablissement.label) icon = createEmojiIcon('🏆', 'label-icon');
        else if (etablissement.visite) icon = createEmojiIcon('✅', 'visited-icon');
        else icon = createEmojiIcon('❌', 'unvisited-icon');
        if (etablissement.latitude && etablissement.longitude) {
            const marker = L.marker(
                [etablissement.latitude, etablissement.longitude],
                { icon: icon, title: etablissement.nom }
            )
            .addTo(map)
            .bindPopup(`
                <div class="infowindow-content">
                    <h4>${etablissement.nom}</h4>
                    <p>${etablissement.adresse}, ${etablissement.ville}</p>
                    <a href="${baseUrl}/etablissement/${etablissement.id_etab}" class="btn btn-sm btn-success">Voir plus</a>
                </div>
            `);
            marker.options.etablissement = etablissement; // Ajouter les données de l'établissement au marqueur
            markers.push(marker);
            bounds.extend(marker.getLatLng());
        } else {
            console.warn(`Établissement sans coordonnées valides: ${etablissement.nom}`);
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
    document.getElementById('filter-all').addEventListener('click', function() {
        activeFilters = { type_pate: false, visited: false, unvisited: false, label: false };
        updateMarkersBasedOnFilters();
        document.getElementById('sub-filters').classList.remove('show');
    });

    // Bouton pour afficher/masquer les options de pâte
    document.getElementById('filter-pate-btn').addEventListener('click', function() {
        const subFilters = document.getElementById('sub-filters');
        // Si les sous-filtres sont déjà visibles et proviennent de ce bouton, on les masque
        if (subFilters.classList.contains('show') &&
            subFilters.querySelector('.filter-group label')?.textContent === 'Pâte') {
            subFilters.classList.remove('show');
        } else {
            subFilters.innerHTML = `
                <div class="filter-group">
                   
                    <button id="filter-type_pate_FEUILLETEE" class="btn btn-secondary">Feuilletée</button>
                    <button id="filter-type_pate_BRISEE" class="btn btn-secondary">Brisée</button>
                    <button id="filter-type_pate_SUCREE" class="btn btn-secondary">Sucrée</button>
                    <button id="filter-type_pate_SABLEE" class="btn btn-secondary">Sablée</button>
                    <button id="filter-type_pate_MIXTE" class="btn btn-secondary">Mixte</button>
                </div>
            `;
            subFilters.classList.add('show');
            setupPateButtons();
        }
    });

    // Bouton pour afficher/masquer les options de statut
    document.getElementById('filter-statut-btn').addEventListener('click', function() {
        const subFilters = document.getElementById('sub-filters');
        // Si les sous-filtres sont déjà visibles et proviennent de ce bouton, on les masque
        if (subFilters.classList.contains('show') &&
            subFilters.querySelector('.filter-group label')?.textContent === 'Statut') {
            subFilters.classList.remove('show');
        } else {
            subFilters.innerHTML = `
                <div class="filter-group">
                    <button id="filter-visited" class="btn btn-success">Visités</button>
                    <button id="filter-unvisited" class="btn btn-danger">Non visités</button>
                    <button id="filter-label" class="btn btn-warning">Avec label</button>
                </div>
            `;
            subFilters.classList.add('show');
            setupStatutButtons();
        }
    });

    // Fonction pour configurer les boutons de pâte
    function setupPateButtons() {
        document.getElementById('filter-type_pate_FEUILLETEE').addEventListener('click', function() {
            activeFilters.type_pate = activeFilters.type_pate === 'Feuilletée' ? false : 'Feuilletée';
            activeFilters.visited = false;
            activeFilters.unvisited = false;
            activeFilters.label = false;
            updateMarkersBasedOnFilters();
        });

        document.getElementById('filter-type_pate_BRISEE').addEventListener('click', function() {
            activeFilters.type_pate = activeFilters.type_pate === 'Brisée' ? false : 'Brisée';
            activeFilters.visited = false;
            activeFilters.unvisited = false;
            activeFilters.label = false;
            updateMarkersBasedOnFilters();
        });

        document.getElementById('filter-type_pate_SUCREE').addEventListener('click', function() {
            activeFilters.type_pate = activeFilters.type_pate === 'Sucrée' ? false : 'Sucrée';
            activeFilters.visited = false;
            activeFilters.unvisited = false;
            activeFilters.label = false;
            updateMarkersBasedOnFilters();
        });

        document.getElementById('filter-type_pate_SABLEE').addEventListener('click', function() {
            activeFilters.type_pate = activeFilters.type_pate === 'Sablée' ? false : 'Sablée';
            activeFilters.visited = false;
            activeFilters.unvisited = false;
            activeFilters.label = false;
            updateMarkersBasedOnFilters();
        });

        document.getElementById('filter-type_pate_MIXTE').addEventListener('click', function() {
            activeFilters.type_pate = activeFilters.type_pate === 'Mixte' ? false : 'Mixte';
            activeFilters.visited = false;
            activeFilters.unvisited = false;
            activeFilters.label = false;
            updateMarkersBasedOnFilters();
        });
    }

    // Fonction pour configurer les boutons de statut
    function setupStatutButtons() {
        document.getElementById('filter-visited').addEventListener('click', function() {
            activeFilters.visited = !activeFilters.visited;
            activeFilters.type_pate = false;
            activeFilters.unvisited = false;
            activeFilters.label = false;
            updateMarkersBasedOnFilters();
        });

        document.getElementById('filter-unvisited').addEventListener('click', function() {
            activeFilters.unvisited = !activeFilters.unvisited;
            activeFilters.type_pate = false;
            activeFilters.visited = false;
            activeFilters.label = false;
            updateMarkersBasedOnFilters();
        });

        document.getElementById('filter-label').addEventListener('click', function() {
            activeFilters.label = !activeFilters.label;
            activeFilters.type_pate = false;
            activeFilters.visited = false;
            activeFilters.unvisited = false;
            updateMarkersBasedOnFilters();
        });
    }
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
    initMap();
    updateMapAndMarkers();
    initAutocomplete();
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

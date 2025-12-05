// Variables globales (déclarées une seule fois)
let autocomplete;
let map;
let markers = [];
let etablissements = [];
let isAdmin = window.isAdmin || false;
let googleMapsApiKey = window.googleMapsApiKey || '';
let csrfToken = window.csrfToken || '';
let visite = (window.filterSettings && window.filterSettings.visite) || false;
let labellise = (window.filterSettings && window.filterSettings.labellise) || false;
let activeFilters = (window.filterSettings && window.filterSettings.activeFilters) || { type_pate: 'tous', type_saveur: 'tous', prix: 'tous' };
let nom = (window.filterSettings && window.filterSettings.nom) || '';

// Fonction utilitaire pour limiter le nombre de requêtes (debounce)
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Mise à jour sécurisée du texte du bouton principal
function updateMainButton(filterType, value) {
    const btn = document.querySelector(`#${filterType}-btn`);
    if (!btn) {
        console.error(`Bouton #${filterType}-btn introuvable`);
        return;
    }
    if (!window.filterLabels || !window.filterLabels[filterType] || !window.filterLabels[filterType][value]) {
        console.error(`Label introuvable pour ${filterType}=${value}`);
        return;
    }
    btn.textContent = window.filterLabels[filterType][value];
}

// Fonction pour filtrer les établissements
function filterEtablissements() {
    const { type_pate, type_saveur, prix } = activeFilters;
    return window.etablissementsInitiaux.filter(etab => {
        return (
            (type_pate === 'tous' || etab.type_pate === type_pate) &&
            (type_saveur === 'tous' || etab.type_saveur === type_saveur) &&
            (prix === 'tous' ||
             (prix === '0' && parseFloat(etab.prix) < 2.5) ||
             (prix === '2.5' && parseFloat(etab.prix) >= 2.5 && parseFloat(etab.prix) < 5) ||
             (prix === '5' && parseFloat(etab.prix) >= 5))
        );
    });
}

// Gestion des clics sur les boutons principaux et options de filtre
document.addEventListener('DOMContentLoaded', function() {
    // Gestion des boutons principaux
    document.querySelectorAll('.filter-main-btn').forEach(mainBtn => {
        mainBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const filterType = this.getAttribute('data-filter');
            const options = document.querySelector(`.filter-options[data-filter="${filterType}"]`);
            document.querySelectorAll('.filter-options').forEach(opt => {
                if (opt !== options) opt.style.display = 'none';
            });
            options.style.display = options.style.display === 'block' ? 'none' : 'block';
        });
    });

    // Fermer les menus si clic ailleurs
    document.addEventListener('click', function() {
        document.querySelectorAll('.filter-options').forEach(opt => {
            opt.style.display = 'none';
        });
    });

    // Gestion de la sélection des options
    document.querySelectorAll('.filter-option').forEach(option => {
        option.addEventListener('click', function(e) {
            e.stopPropagation();
            const filterType = this.getAttribute('data-filter');
            const value = this.getAttribute('data-value');
            document.querySelectorAll(`.filter-option[data-filter="${filterType}"]`).forEach(opt => {
                opt.classList.remove('active');
            });
            this.classList.add('active');
            updateMainButton(filterType, value);
            this.parentElement.style.display = 'none';
            activeFilters[filterType] = value;
            updateMapAndMarkers();
        });
    });
});

// Fonction pour recharger les établissements selon les filtres
async function loadEtablissements() {
    try {
        document.getElementById('loading-spinner').style.display = 'block';
        const params = new URLSearchParams();
        const urlParams = new URLSearchParams(window.location.search);
        const ville = urlParams.get('ville');
        const type_flan = urlParams.get('type');
        if (ville) params.append('ville', ville);
        if (type_flan) params.append('type_flan', type_flan);
        if (nom) params.append('nom', nom);
        if (visite) params.append('visite', visite);
        if (labellise) params.append('labellise', labellise);
        if (activeFilters.type_pate && activeFilters.type_pate !== 'tous') params.append('type_pate', activeFilters.type_pate);
        if (activeFilters.type_saveur && activeFilters.type_saveur !== 'tous') params.append('type_saveur', activeFilters.type_saveur);
        if (activeFilters.prix && activeFilters.prix !== 'tous') params.append('prix', activeFilters.prix);
        const response = await fetch(`/api/etablissements?${params.toString()}`);
        if (!response.ok) throw new Error("Erreur lors du chargement des établissements.");
        return await response.json();
    } catch (error) {
        console.error("Erreur:", error);
        return [];
    } finally {
        document.getElementById('loading-spinner').style.display = 'none';
    }
}

// Fonction pour mettre à jour la carte avec de nouveaux établissements
async function updateMapAndMarkers() {
    const newEtablissements = await loadEtablissements();
    if (!newEtablissements || newEtablissements.length === 0) {
        console.warn("Aucun établissement trouvé avec ces filtres.");
        return;
    }
    if (markers.length > 0) {
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];
    }
    etablissements = newEtablissements;
    const bounds = L.latLngBounds();
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
    etablissements.forEach(etablissement => {
        let icon = nonvisiteIcon;
        if (etablissement.label) {
            icon = labelIcon;
        } else if (etablissement.visite) {
            icon = visiteIcon;
        }
        const marker = L.marker([etablissement.latitude, etablissement.longitude], {
            icon: icon,
            title: etablissement.nom
        })
        .addTo(map)
        .bindPopup(window.infowindowContents[etablissement.id_etab] || "Détails non disponibles");
        markers.push(marker);
        bounds.extend(marker.getLatLng());
    });
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
        console.log("Élément #search absent : pas d'autocomplete.");
        return;
    }
    if (!googleMapsApiKey) {
        console.error("Clé API Google Maps manquante pour l'autocomplete.");
        return;
    }
    autocomplete = new google.maps.places.Autocomplete(input, {
        types: ['establishment'],
        componentRestrictions: {country: 'fr'}
    });
    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        if (!place.geometry) return;
        document.getElementById('ajout-etab-nom').value = place.name || '';
        document.getElementById('ajout-etab-adresse').value = place.formatted_address || '';
        document.getElementById('ajout-etab-latitude').value = place.geometry.location.lat();
        document.getElementById('ajout-etab-longitude').value = place.geometry.location.lng();
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
        return;
    }
    map = L.map('map').setView([46.2276, 2.2137], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'info legend');
        div.innerHTML = `🏆 Labellisé ✅ Visité ❌ Non visité`;
        return div;
    };
    legend.addTo(map);
    updateMapAndMarkers();
};

// Fonction pour initialiser l'autocomplétion et la carte
window.initAll = function() {
    if (!googleMapsApiKey) {
        console.error("Clé API Google Maps manquante ou invalide. L'autocomplete ne fonctionnera pas.");
    }
    initMap();
    initAutocomplete();
};

// Chargement de l'API Google Maps (si clé valide)
document.addEventListener('DOMContentLoaded', function() {
    if (googleMapsApiKey) {
        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&libraries=places&callback=initAll&v=weekly`;
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
    } else {
        console.error("Clé API Google Maps non définie. L'autocomplete ne sera pas disponible.");
        initMap(); // Initialise au moins la carte
    }
});

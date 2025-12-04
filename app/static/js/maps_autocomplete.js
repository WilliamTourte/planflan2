// Variables globales
let autocomplete;
let map;
let markers = [];
let etablissements = [];
let isAdmin = window.isAdmin;
let googleMapsApiKey = window.googleMapsApiKey;
let csrfToken = window.csrfToken;
let nom = window.filterSettings.nom;
let visite = window.filterSettings.visite;
let labellise = window.filterSettings.labellise;
let activeFilters = window.filterSettings.activeFilters;

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
async function loadEtablissements() {
    try {
        document.getElementById('loading-spinner').style.display = 'block';
        const params = new URLSearchParams();
        // Récupère les paramètres de recherche depuis l'URL
        const urlParams = new URLSearchParams(window.location.search);
        const ville = urlParams.get('ville');
        const type_flan = urlParams.get('type');

        // Ajoute les filtres de recherche à la requête API
        if (ville) params.append('ville', ville);
        if (type_flan) params.append('type_flan', type_flan);
        // Ajoute les autres filtres existants
        if (nom) params.append('nom', nom);
        if (visite) params.append('visite', visite);
        if (labellise) params.append('labellise', labellise);
        if (activeFilters.type_pate !== 'tous') params.append('type_pate', activeFilters.type_pate);
        if (activeFilters.type_saveur !== 'tous') params.append('type_saveur', activeFilters.type_saveur);
        if (activeFilters.prix !== 'tous') params.append('prix', activeFilters.prix);

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

    // Efface les anciens marqueurs
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    // Met à jour les données globales
    etablissements = newEtablissements;

    // Réutilise la logique d'initialisation des marqueurs
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
            title: etablissement.nom
        })
        .addTo(map)
        .bindPopup(window.infowindowContents[etablissement.id_etab] || "Détails non disponibles");
        markers.push(marker);
        bounds.extend(marker.getLatLng());
    });

    // Ajuste la vue
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

    // Légende
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'info legend');
        div.innerHTML = `🏆 Labellisé ✅ Visité ❌ Non visité`;
        return div;
    };
    legend.addTo(map);

    // Charge les établissements initiaux
    updateMapAndMarkers();
};

// Écouteurs pour les bulles de filtre
document.addEventListener('DOMContentLoaded', function() {
    // Écouteurs pour les bulles de filtre
    document.querySelectorAll('.filter-bubble').forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.dataset.filter;
            const value = this.dataset.value;
            // Met à jour les filtres actifs
            activeFilters[filter] = value;
            // Met à jour l'apparence des boutons
            document.querySelectorAll(`.filter-bubble[data-filter="${filter}"]`).forEach(b => {
                b.classList.remove('active');
            });
            this.classList.add('active');
            // Met à jour la carte
            updateMapAndMarkers();
        });
    });

    // Écouteurs pour les filtres existants
    const nomFilter = document.getElementById('filter-nom');
    const visiteFilter = document.getElementById('filter-visite');
    const labelliseFilter = document.getElementById('filter-labellise');
    if (nomFilter) {
        nomFilter.addEventListener('input', debounce(function() {
            nom = this.value;
            updateMapAndMarkers();
        }, 500));
    }
    if (visiteFilter) {
        visiteFilter.addEventListener('change', function() {
            visite = this.value;
            updateMapAndMarkers();
        });
    }
    if (labelliseFilter) {
        labelliseFilter.addEventListener('change', function() {
            labellise = this.value;
            updateMapAndMarkers();
        });
    }

    // Chargement de l'API Google Maps (uniquement pour l'autocomplete)
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&libraries=places&callback=initAll&v=weekly&loading=async`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
});

// Fonction pour initialiser l'autocomplétion et la carte
window.initAll = function() {
    initAutocomplete();
    initMap();
};

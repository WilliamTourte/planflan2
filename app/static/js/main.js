/**
 * Point d'entrée principal pour l'application PlanFlan
 * 
 * Ce module coordonne l'initialisation de tous les modules JavaScript
 */

// Import des modules
import * as utils from './utils.js';
import { GeolocationHandler, getUserLocationSimple } from './geolocation.js';
import * as mapModule from './map.js';
import * as filters from './filters.js';
import * as autocomplete from './autocomplete.js';
import * as api from './api.js';
import * as macros from './macros.js';
import { showDeleteAccountForm } from './dashboard.js';
import { initializePasswordToggles } from './password-toggle.js';

// Initialisation globale
document.addEventListener('DOMContentLoaded', function() {
    console.log("Initialisation de l'application PlanFlan...");
    
    // Initialisation selon la page
    const pageType = document.body.getAttribute('data-page-type');
    console.log("Type de page détecté:", pageType);
    
    switch(pageType) {
        case 'home':
            initializeHomePage();
            break;
        case 'liste_etablissements':
            initializeListeEtablissementsPage();
            break;
        case 'proposer_etablissement':
            initializeProposerEtablissementPage();
            break;
        case 'dashboard':
            initializeDashboardPage();
            break;
        default:
            initializeDefaultPage();
    }
    
    // Initialisation commune
    utils.restoreStateFromUrl();
    console.log("Initialisation commune terminée");
});

/**
 * Initialisation pour la page d'accueil
 */
function initializeHomePage() {
    console.log("Initialisation de la page d'accueil");
    
    // Initialiser l'autocomplete pour les villes
    if (!autocomplete.initAutocomplete()) {
        console.log("Fallback to DOMContentLoaded for autocomplete");
        document.addEventListener("DOMContentLoaded", autocomplete.initAutocomplete);
    }
    
    // Initialiser le bouton de géolocalisation
    initGeolocButton();
}

/**
 * Initialisation pour la page de liste des établissements
 */
function initializeListeEtablissementsPage() {
    console.log("Initialisation de la page de liste des établissements");
    
    // Récupérer les données des établissements
    const etablissementsDataElement = document.getElementById('etablissements-data');
    const etablissementsData = etablissementsDataElement ? JSON.parse(etablissementsDataElement.getAttribute('data-etablissements') || '[]') : [];
    
    const isAdminElement = document.getElementById('is-admin');
    const isAdmin = isAdminElement ? JSON.parse(isAdminElement.getAttribute('data-is-admin') || 'false') : false;
    
    const googleMapsApiKeyElement = document.getElementById('google-maps-api-key');
    const googleMapsApiKey = googleMapsApiKeyElement ? googleMapsApiKeyElement.getAttribute('data-api-key') || '' : '';

    // Ajout des coordonnées utilisateur si disponibles
    const userLocationElement = document.getElementById('user-location');
    const userLat = userLocationElement ? parseFloat(userLocationElement.getAttribute('data-lat')) : null;
    const userLon = userLocationElement ? parseFloat(userLocationElement.getAttribute('data-lon')) : null;

    // Ajout de la ville sélectionnée si disponible
    const villeSelectionneeElement = document.getElementById('ville-selectionnee');
    const villeSelectionnee = villeSelectionneeElement ? villeSelectionneeElement.getAttribute('data-ville') : null;

    // Configurer la position utilisateur dans le module map
    if (userLat && userLon) {
        mapModule.setUserLocation({ lat: userLat, lon: userLon });
    }
    
    if (villeSelectionnee) {
        mapModule.setVilleSelectionnee(villeSelectionnee);
    }

    // Initialiser la carte et les filtres
    mapModule.initMap();
    mapModule.updateMapAndMarkers();
    filters.setupFilterButtons();
    
    // Vérifier si on vient d'une géolocalisation depuis la page d'accueil
    const urlParams = new URLSearchParams(window.location.search);
    const fromGeoloc = urlParams.get('geolocalisation') === 'true';
    const fromVilleSelection = urlParams.get('from_ville_selection') === 'true';

    // Restaurer l'état depuis l'URL
    const restoredFilters = filters.restoreFiltersFromUrl();
    mapModule.setActiveFilters(restoredFilters);
    
    // Mettre à jour les boutons pour refléter l'état restauré
    utils.updateActiveButtonStates(restoredFilters);
    utils.updateMainFilterButtons(restoredFilters);
    
    // Si on vient d'une géolocalisation, forcer l'affichage du marqueur utilisateur
    if (fromGeoloc && userLat && userLon) {
        mapModule.createUserMarker(true); // forceZoom = true
    }
    
    // Si on vient d'une sélection de ville, centrer la carte sur les coordonnées
    if (fromVilleSelection && userLat && userLon) {
        mapModule.setView([userLat, userLon], 13);
    }
    
    // Sauvegarder l'état initial
    mapModule.saveCompleteStateToUrl();
}

/**
 * Initialisation pour la page de proposition d'établissement
 */
function initializeProposerEtablissementPage() {
    console.log("Initialisation de la page de proposition d'établissement");
    
    const googleMapsApiKeyElement = document.getElementById('google-maps-api-key');
    if (!googleMapsApiKeyElement) {
        console.error("Élément #google-maps-api-key introuvable !");
        return;
    }
    const googleMapsApiKey = googleMapsApiKeyElement.getAttribute('data-api-key');
    
    // Initialiser l'autocomplete pour les villes (uniquement pour le champ ville)
    const villeAutocompleteInitialized = autocomplete.initAutocomplete();
    if (villeAutocompleteInitialized) {
        console.log("Autocomplete pour les villes initialisé avec succès");
        
        // Ajouter un écouteur pour le champ ville
        const villeInput = document.getElementById('ville-autocomplete');
        if (villeInput) {
            villeInput.addEventListener('villeSelected', function(e) {
                const selectedVille = e.detail.ville;
                console.log("Ville sélectionnée:", selectedVille);
                
                // Mettre à jour le champ caché ville
                const hiddenVilleField = document.getElementById('ajout-etab-ville');
                if (hiddenVilleField) {
                    hiddenVilleField.value = selectedVille;
                }
                
                // Réinitialiser le champ de recherche d'établissement
                const searchInput = document.getElementById('search');
                if (searchInput) {
                    searchInput.value = '';
                    searchInput.focus();
                }
                
                // Recharger l'autocomplete Google Places avec restriction à la ville sélectionnée
                if (selectedVille) {
                    console.log("DEBUG: Ville sélectionnée dans main.js:", selectedVille);
                    
                    // Nettoyer le feedback précédent
                    autocomplete.clearCityRestrictionFeedback();
                    
                    // Initialiser avec restriction à la ville
                    autocomplete.initGooglePlacesAutocompleteWithCity('search', googleMapsApiKey, selectedVille)
                        .then(autocompleteInstance => {
                            console.log("DEBUG: Google Places Autocomplete initialisé avec restriction à la ville:", selectedVille);
                            window.autocompleteInstance = autocompleteInstance;
                            utils.showToast('Recherche restreinte à ' + selectedVille, 'info');
                        })
                        .catch(error => {
                            console.error("DEBUG: Erreur lors de l'initialisation de Google Places Autocomplete:", error);
                            utils.showToast(error.message, 'error');
                        });
                }
            });
        }
    }
    
    // Initialiser l'autocomplete Google Places par défaut (sans ville)
    // Mais seulement si aucune ville n'est déjà sélectionnée
    const villeInput = document.getElementById('ville-autocomplete');
    if (!villeInput || villeInput.value === '') {
        autocomplete.initGooglePlacesAutocomplete('search', googleMapsApiKey)
            .then(autocompleteInstance => {
                console.log("Google Places Autocomplete initialisé avec succès (mode global)");
                window.autocompleteInstance = autocompleteInstance;
            })
            .catch(error => {
                console.error("Erreur lors de l'initialisation de Google Places Autocomplete:", error);
                utils.showToast(error.message, 'error');
            });
    }
    
    // Gestion du bouton de réinitialisation de la ville
    const clearVilleBtn = document.getElementById('clear-ville-btn');
    if (clearVilleBtn) {
        clearVilleBtn.addEventListener('click', function() {
            // Réinitialiser les champs
            const villeInput = document.getElementById('ville-autocomplete');
            const hiddenVilleField = document.getElementById('ajout-etab-ville');
            const searchInput = document.getElementById('search');
            
            if (villeInput) villeInput.value = '';
            if (hiddenVilleField) hiddenVilleField.value = '';
            if (searchInput) {
                searchInput.value = '';
                searchInput.focus();
            }
            
            // Nettoyer le feedback visuel
            autocomplete.clearCityRestrictionFeedback();
            
            // Réinitialiser l'autocomplete des établissements en mode global
            autocomplete.initGooglePlacesAutocomplete('search', googleMapsApiKey)
                .then(autocompleteInstance => {
                    console.log("Autocomplete réinitialisé pour la recherche globale");
                    window.autocompleteInstance = autocompleteInstance;
                    utils.showToast('Recherche réinitialisée pour tous les établissements', 'info');
                })
                .catch(error => {
                    console.error("Erreur lors de la réinitialisation:", error);
                    utils.showToast(error.message, 'error');
                });
        });
    }
    
    // Initialiser la carte avec le marqueur d'infowindow
    // Ajouter un petit délai pour s'assurer que tout est prêt
    setTimeout(() => {
        console.log("Initialisation de la carte après délai...");
        
        // Fonction pour vérifier et attendre Leaflet
        function waitForLeaflet(callback, maxAttempts = 20, delay = 100) {
            let attempts = 0;
            
            function checkLeaflet() {
                attempts++;
                
                console.log("Vérification de Leaflet (attempt " + attempts + "/" + maxAttempts + ")...");
                console.log("L variable:", typeof L);
                
                if (typeof L === 'undefined') {
                    console.error("Leaflet n'est pas encore chargé - L est undefined!");
                    if (attempts < maxAttempts) {
                        setTimeout(checkLeaflet, delay);
                    } else {
                        console.error("Leaflet n'a pas pu être chargé après " + maxAttempts + " tentatives!");
                        utils.showToast("Erreur chargement bibliothèque carte", 'error');
                    }
                    return;
                }
                
                if (typeof L.map !== 'function') {
                    console.error("Leaflet n'est pas chargé correctement - L.map n'est pas une fonction!");
                    console.error("L.map est:", typeof L.map, L.map);
                    if (attempts < maxAttempts) {
                        setTimeout(checkLeaflet, delay);
                    } else {
                        console.error("Leaflet n'a pas pu être chargé correctement après " + maxAttempts + " tentatives!");
                        utils.showToast("Erreur chargement bibliothèque carte", 'error');
                    }
                    return;
                }
                
                // Vérifier que l'élément map existe et est visible
                const mapElement = document.getElementById('map');
                if (!mapElement) {
                    console.error("Élément #map introuvable!");
                    utils.showToast("Élément carte introuvable", 'error');
                    return;
                }
                
                // S'assurer que l'élément est visible
                const computedStyle = window.getComputedStyle(mapElement);
                if (computedStyle.display === 'none' || computedStyle.visibility === 'hidden') {
                    console.error("Élément #map n'est pas visible");
                    utils.showToast("Élément carte non visible", 'error');
                    return;
                }
                
                // S'assurer que l'élément a une taille
                if (mapElement.offsetWidth === 0 || mapElement.offsetHeight === 0) {
                    console.error("Élément #map n'a pas de taille");
                    utils.showToast("Élément carte sans taille", 'error');
                    return;
                }
                
                console.log("Leaflet et élément map sont prêts!");
                callback();
            }
            
            checkLeaflet();
        }
        
        waitForLeaflet(() => {
            // Vérifier que le module map est chargé
            if (typeof mapModule === 'undefined' || typeof mapModule.createInfowindowMarker !== 'function') {
                console.error("Module map n'est pas chargé!");
                utils.showToast("Erreur chargement module carte", 'error');
                return;
            }
            
            initMapWithInfowindow();
        });
    }, 200);
}

/**
 * Initialise la carte avec un marqueur utilisant la nouvelle infowindow modulaire
 */
function initMapWithInfowindow() {
    console.log("Début de initMapWithInfowindow");
    
    // Récupérer les données du formulaire
    const etablissementData = {
        nom: document.getElementById('ajout-etab-nom').value || 'Nouvel établissement',
        adresse: document.getElementById('ajout-etab-adresse').value || '',
        ville: document.getElementById('ajout-etab-ville').value || '',
        latitude: parseFloat(document.getElementById('ajout-etab-latitude').value) || 48.8566,
        longitude: parseFloat(document.getElementById('ajout-etab-longitude').value) || 2.3522,
        type_etab: document.getElementById('ajout-etab-type_etab').value || 'BOULANGERIE'
    };

    console.log("Données de l'établissement:", etablissementData);

    // Initialiser la carte
    const mapElement = document.getElementById("map");
    if (!mapElement) {
        console.error("Élément #map introuvable !");
        utils.showToast("Élément carte introuvable", 'error');
        return;
    }
    
    console.log("Élément map trouvé:", mapElement);
    console.log("Style calculé:", window.getComputedStyle(mapElement));
    console.log("Taille:", { width: mapElement.offsetWidth, height: mapElement.offsetHeight });

    // Vérifier si une carte existe déjà
    let leafletMap = window.map;
    
    if (leafletMap) {
        console.log("Carte existante trouvée, réutilisation...");
        // Nettoyer les marqueurs existants
        try {
            leafletMap.eachLayer(layer => {
                if (layer instanceof L.Marker) {
                    leafletMap.removeLayer(layer);
                }
            });
            // Centrer sur la nouvelle position
            leafletMap.setView([etablissementData.latitude, etablissementData.longitude], 15);
        } catch (e) {
            console.error("Erreur lors du nettoyage de la carte existante:", e);
            leafletMap = null;
        }
    }
    
    // Créer une nouvelle carte si nécessaire
    if (!leafletMap) {
        console.log("Création d'une nouvelle carte pour proposer_etablissement");
        
        // S'assurer que l'élément est visible et a une taille
        const computedStyle = window.getComputedStyle(mapElement);
        if (computedStyle.display === 'none' || computedStyle.visibility === 'hidden') {
            console.error("Élément #map n'est pas visible");
            utils.showToast("Élément carte non visible", 'error');
            return;
        }
        
        // S'assurer que l'élément a une taille
        if (mapElement.offsetWidth === 0 || mapElement.offsetHeight === 0) {
            console.error("Élément #map n'a pas de taille");
            utils.showToast("Élément carte sans taille", 'error');
            return;
        }
        
        try {
            // S'assurer que l'élément map est visible dans le DOM
            mapElement.style.visibility = 'visible';
            mapElement.style.display = 'block';
            mapElement.style.height = '55vh';
            mapElement.style.width = '100%';
            
            console.log("Création de la carte Leaflet...");
            
            // Créer la carte Leaflet
            leafletMap = L.map('map').setView([etablissementData.latitude, etablissementData.longitude], 15);
            
            // Vérifier que la carte Leaflet a été correctement créée
            if (!leafletMap || typeof leafletMap.addLayer !== 'function') {
                console.error("La carte Leaflet n'a pas été correctement créée", leafletMap);
                utils.showToast("Erreur création carte Leaflet", 'error');
                return;
            }
            
            // Ajouter les tuiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(leafletMap);
            
            // Assigner la carte Leaflet à window.map
            window.map = leafletMap;
            
            console.log("Carte créée avec succès", window.map);
        } catch (e) {
            console.error("Erreur lors de la création de la carte Leaflet:", e);
            utils.showToast("Erreur création carte", 'error');
            return;
        }
    }
    
    // Forcer un redimensionnement pour s'assurer que la carte est correctement affichée
    setTimeout(() => {
        if (leafletMap && leafletMap.invalidateSize) {
            leafletMap.invalidateSize();
        }
    }, 100);

    // Vérification que la carte est prête
    if (!window.map || typeof window.map.addLayer !== 'function') {
        console.error("La carte n'est pas prête pour ajouter des marqueurs");
        utils.showToast("Carte non prête", 'error');
        return;
    }

    // Utiliser la méthode unifiée pour créer le marqueur avec infowindow
    try {
        console.log("Carte prête, création du marqueur...");
        mapModule.createInfowindowMarker(window.map, etablissementData, 'proposition');
    } catch (e) {
        console.error("Erreur lors de la création du marqueur:", e);
        utils.showToast("Erreur création marqueur carte", 'error');
    }

    // Mettre à jour le marqueur lorsque les champs changent
    document.querySelectorAll('.etablissement-hidden-fields input, .etablissement-hidden-fields select').forEach(input => {
        input.addEventListener('change', function() {
            // Mettre à jour les données
            etablissementData.nom = document.getElementById('ajout-etab-nom').value;
            etablissementData.adresse = document.getElementById('ajout-etab-adresse').value;
            etablissementData.ville = document.getElementById('ajout-etab-ville').value;
            etablissementData.latitude = parseFloat(document.getElementById('ajout-etab-latitude').value);
            etablissementData.longitude = parseFloat(document.getElementById('ajout-etab-longitude').value);
            etablissementData.type_etab = document.getElementById('ajout-etab-type_etab').value;

            // Supprimer l'ancien marqueur et en créer un nouveau
            if (window.map && typeof window.map.eachLayer === 'function') {
                try {
                    window.map.eachLayer(layer => {
                        if (layer instanceof L.Marker) {
                            window.map.removeLayer(layer);
                        }
                    });
                    // Recréer le marqueur avec les nouvelles données
                    try {
                        if (typeof window.map.addLayer === 'function') {
                            console.log("Carte prête pour recréation du marqueur...");
                            mapModule.createInfowindowMarker(window.map, etablissementData, 'proposition');
                        } else {
                            console.error("La carte n'est pas prête pour la recréation du marqueur");
                            utils.showToast("Carte non prête", 'error');
                        }
                    } catch (e) {
                        console.error("Erreur lors de la recréation du marqueur:", e);
                        utils.showToast("Erreur recréation marqueur", 'error');
                    }
                } catch (e) {
                    console.error("Erreur lors de la mise à jour du marqueur:", e);
                    utils.showToast("Erreur mise à jour carte", 'error');
                }
            } else {
                console.error("Impossible de mettre à jour le marqueur - carte non initialisée");
                utils.showToast("Carte non initialisée", 'error');
            }
        });
    });
}

/**
 * Configure l'autocomplete personnalisé pour les établissements dans une ville spécifique
 */
function setupCustomEtablissementAutocomplete(inputId, villeName) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    // Supprimer les écouteurs existants
    const newInput = input.cloneNode(true);
    input.parentNode.replaceChild(newInput, input);
    
    // Ajouter un écouteur pour rechercher des établissements dans la ville
    newInput.addEventListener('input', utils.debounce(function() {
        if (this.value.length > 2) { // Attendre au moins 3 caractères
            autocomplete.searchEtablissementsByVille(villeName, this.value)
                .then(results => {
                    autocomplete.showEtablissementResults(results, inputId);
                })
                .catch(error => {
                    console.error("Erreur de recherche:", error);
                    utils.showToast(error.message, 'error');
                });
        } else {
            // Masquer les résultats si la requête est trop courte
            const resultsContainer = document.getElementById(`${inputId}-results`);
            if (resultsContainer) {
                resultsContainer.style.display = 'none';
            }
        }
    }, 300));
    
    // Gestion du clic en dehors pour fermer les résultats
    document.addEventListener('click', function(e) {
        if (e.target !== newInput) {
            const resultsContainer = document.getElementById(`${inputId}-results`);
            if (resultsContainer) {
                resultsContainer.style.display = 'none';
            }
        }
    });
}

/**
 * Initialisation pour la page de tableau de bord
 */
function initializeDashboardPage() {
    console.log("Initialisation de la page de tableau de bord");
    
    // Initialiser les boutons toggle mot de passe
    initializePasswordToggles();
    
    // Vérifier si on vient d'une erreur de suppression de compte
    if (window.location.search.includes("error=")) {
        showDeleteAccountForm();
    }
    
    // Configurer les boutons du dashboard
    setupDashboardButtons();
}

/**
 * Initialisation par défaut pour les autres pages
 */
function initializeDefaultPage() {
    console.log("Initialisation par défaut pour la page actuelle");
    
    // Logique commune à toutes les pages
    setupCommonElements();
    initializePasswordToggles();
}

/**
 * Fonction pour initialiser le bouton de géolocalisation
 */
function initGeolocButton() {
    const geolocButton = document.getElementById("geoloc-button");
    if (!geolocButton) return;

    geolocButton.addEventListener("click", function () {
        // Sauvegarder l'état initial du bouton
        const originalHTML = geolocButton.innerHTML;
        const originalDisabled = geolocButton.disabled;

        // Désactiver le bouton et montrer un indicateur de chargement
        geolocButton.innerHTML =
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        geolocButton.disabled = true;

        // Utiliser la fonction légère de géolocalisation
        getUserLocationSimple()
            .then((position) => {
                // Remplir les champs cachés avec les coordonnées
                const latitudeField = document.querySelector('input[name="latitude"]');
                const longitudeField = document.querySelector('input[name="longitude"]');

                if (latitudeField && longitudeField) {
                    latitudeField.value = position.coords.latitude;
                    longitudeField.value = position.coords.longitude;

                    // Construire l'URL avec les coordonnées et le flag de géolocalisation
                    const url = new URL(window.location.origin + '/liste_etablissements');
                    url.searchParams.append("latitude", position.coords.latitude);
                    url.searchParams.append("longitude", position.coords.longitude);
                    url.searchParams.append("geolocalisation", "true");

                    window.location.href = url.toString();
                    return; // Ne pas soumettre le formulaire
                } else {
                    restoreButtonState();
                }
            })
            .catch((error) => {
                // Gérer les erreurs de géolocalisation
                let errorMessage = "Erreur de géolocalisation: ";
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage += "Permission refusée";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage += "Position indisponible";
                        break;
                    case error.TIMEOUT:
                        errorMessage += "Timeout";
                        break;
                    default:
                        errorMessage += error.message;
                }

                showToast(errorMessage, 'error');
                restoreButtonState();
            });

        /**
         * Restaure l'état initial du bouton de géolocalisation.
         */
        function restoreButtonState() {
            geolocButton.innerHTML = originalHTML;
            geolocButton.disabled = originalDisabled;
        }
    });
}



/**
 * Fonction pour configurer les boutons du dashboard
 */
function setupDashboardButtons() {
    // Bouton d'édition du profil
    const editProfileBtn = document.getElementById("edit-profile-btn");
    if (editProfileBtn) {
        editProfileBtn.addEventListener("click", function () {
            const userInfo = document.getElementById("user-info");
            if (userInfo) userInfo.style.display = "none";
            const editProfileForm = document.getElementById("edit-profile-form");
            if (editProfileForm) editProfileForm.style.display = "block";
        });
    }

    // Bouton d'annulation de l'édition du profil
    const cancelEditBtn = document.getElementById("cancel-edit-btn");
    if (cancelEditBtn) {
        cancelEditBtn.addEventListener("click", function () {
            const userInfo = document.getElementById("user-info");
            if (userInfo) userInfo.style.display = "block";
            const editProfileForm = document.getElementById("edit-profile-form");
            if (editProfileForm) editProfileForm.style.display = "none";
        });
    }


}



/**
 * Fonction pour configurer les éléments communs
 */
function setupCommonElements() {
    // Logique pour alterner entre recherche simple et complexe
    const searchButton = document.getElementById('search-button');
    if (searchButton) {
        searchButton.addEventListener('click', function(event) {
            const searchInput = document.getElementById('search-input');
            const form = event.target.closest('form');

            // Si le champ est vide, redirige vers la route "rechercher"
            if (searchInput.value.trim() === '') {
                event.preventDefault(); // Empêche la soumission du formulaire
                window.location.href = "/rechercher";
            }
        });
    }
}

// Export pour compatibilité avec les anciens scripts
window.utils = utils;
window.mapModule = mapModule;
window.filters = filters;
window.autocomplete = autocomplete;
window.api = api;
window.macros = macros;
window.GeolocationHandler = GeolocationHandler;
window.getUserLocationSimple = getUserLocationSimple;
window.initMapWithInfowindow = initMapWithInfowindow;

// Initialize macros event listeners when main module loads
if (macros && typeof macros.initMacroEventListeners === 'function') {
    macros.initMacroEventListeners();
}

// Export pour les tests
export { initGeolocButton };

// Export des fonctions de macros pour les tests
export { 
  editEtablissement, 
  cancelEdit, 
  editFlan, 
  cancelEditFlan, 
  editEvaluation, 
  cancelEditEval,
  initMacroEventListeners 
} from './macros.js';

// La fonction est définie dans ce fichier, pas importée
export { initMapWithInfowindow };

console.log("Modules PlanFlan chargés et prêts");
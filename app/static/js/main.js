/**
 * Point d'entrée principal pour l'application PlanFlan
 * 
 * Ce module coordonne l'initialisation de tous les modules JavaScript
 */

// Import des modules
import * as utils from './utils.js';
import { GeolocationHandler, getUserLocationSimple } from './geolocation.js';
import * as map from './map.js';
import * as filters from './filters.js';
import * as autocomplete from './autocomplete.js';
import * as api from './api.js';

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
        map.setUserLocation({ lat: userLat, lon: userLon });
    }
    
    if (villeSelectionnee) {
        map.setVilleSelectionnee(villeSelectionnee);
    }

    // Initialiser la carte et les filtres
    map.initMap();
    map.updateMapAndMarkers();
    filters.setupFilterButtons();
    
    // Vérifier si on vient d'une géolocalisation depuis la page d'accueil
    const urlParams = new URLSearchParams(window.location.search);
    const fromGeoloc = urlParams.get('geolocalisation') === 'true';

    // Restaurer l'état depuis l'URL
    const restoredFilters = filters.restoreFiltersFromUrl();
    map.setActiveFilters(restoredFilters);
    
    // Mettre à jour les boutons pour refléter l'état restauré
    utils.updateActiveButtonStates(restoredFilters);
    utils.updateMainFilterButtons(restoredFilters);
    
    // Si on vient d'une géolocalisation, forcer l'affichage du marqueur utilisateur
    if (fromGeoloc && userLat && userLon) {
        map.createUserMarker(true); // forceZoom = true
    }
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
    
    // Initialiser l'autocomplete Google Places
    autocomplete.initGooglePlacesAutocomplete('search', googleMapsApiKey)
        .then(autocompleteInstance => {
            console.log("Google Places Autocomplete initialisé avec succès");
            window.autocompleteInstance = autocompleteInstance;
        })
        .catch(error => {
            console.error("Erreur lors de l'initialisation de Google Places Autocomplete:", error);
            showToast(error.message, 'error');
        });
}

/**
 * Initialisation pour la page de tableau de bord
 */
function initializeDashboardPage() {
    console.log("Initialisation de la page de tableau de bord");
    
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
 * Fonction pour afficher le formulaire de suppression de compte
 */
function showDeleteAccountForm() {
    const deleteSection = document.getElementById("delete-account-section");
    if (deleteSection) {
        deleteSection.style.display = "block";
    }
    const passwordField = document.getElementById("delete-password");
    if (passwordField) {
        passwordField.focus();
    }
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

    // Bouton d'annulation de la suppression de compte
    const cancelDeleteBtn = document.getElementById("cancel-delete-btn");
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener("click", function () {
            cancelDeleteAccount();
        });
    }
}

/**
 * Fonction pour annuler la suppression de compte
 */
function cancelDeleteAccount() {
    const deleteAccountSection = document.getElementById("delete-account-section");
    if (deleteAccountSection) {
        deleteAccountSection.style.display = "none";
    }
    // Supprimer les paramètres d'erreur de l'URL
    const url = new URL(window.location.href);
    url.searchParams.delete("error");
    window.history.replaceState({}, "", url);
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
window.map = map;
window.filters = filters;
window.autocomplete = autocomplete;
window.api = api;
window.GeolocationHandler = GeolocationHandler;
window.getUserLocationSimple = getUserLocationSimple;

console.log("Modules PlanFlan chargés et prêts");
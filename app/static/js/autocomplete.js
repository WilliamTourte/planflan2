/**
 * Module d'autocomplete pour l'application PlanFlan
 * 
 * Ce module gère les fonctionnalités d'autocomplete pour les villes et les établissements
 */

import { debounce, showLoading, hideLoading, showToast } from './utils.js';
import { initMapWithMarker } from './map.js';

/**
 * Initialise le système d'autocomplétion pour la recherche de villes.
 * Configure les événements et les fonctions nécessaires pour l'autocomplétion.
 * @param {object} options - Options de configuration
 * @returns {boolean} True si l'initialisation a réussi, false sinon
 */
export function initAutocomplete(options = {}) {
    const input = document.getElementById("ville-autocomplete");
    const resultsContainer = document.getElementById("autocomplete-results");
    let currentFocus = -1;

    if (!input || !resultsContainer) {
        console.log("Elements not found yet, waiting for DOM...");
        return false;
    }

    console.log("Elements found, initializing autocomplete");

    /**
     * Synchronise la valeur du champ de recherche avec le champ caché du formulaire.
     */
    function syncWithHiddenField() {
        const hiddenField = document.querySelector('input[name="ville"]');
        if (hiddenField) {
            console.log("Syncing hidden field with:", input.value);
            hiddenField.value = input.value;
        } else {
            console.warn("Hidden ville field not found");
        }
    }

    /**
     * Affiche les résultats de recherche des villes.
     * @param {Array<string>} villes - Liste des villes trouvées
     */
    function showResults(villes) {
        console.log("showResults called with:", villes);
        resultsContainer.innerHTML = "";

        if (villes.length === 0) {
            const noResults = document.createElement("div");
            noResults.className = "autocomplete-no-results";
            noResults.textContent = "Aucun flan pour cette ville. \nProposer une adresse ?";
            resultsContainer.appendChild(noResults);
            resultsContainer.classList.add("show");
            return;
        }

        console.log("Showing results for:", villes);
        villes.forEach((ville) => {
            const div = document.createElement("div");
            div.className = "autocomplete-item";
            div.textContent = ville;
            div.addEventListener("click", function () {
                input.value = ville;
                const hiddenField = document.querySelector('input[name="ville"]');
                if (hiddenField) {
                    hiddenField.value = ville;
                    console.log("Champ caché ville mis à jour avec :", hiddenField.value);
                } else {
                    console.error("Champ caché ville non trouvé !");
                }
                resultsContainer.classList.remove("show");
                
                // Récupérer les coordonnées GPS pour zoomer sur la carte
                fetch(`/api/villes?q=${encodeURIComponent(ville)}&with_gps=true`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.length > 0) {
                            const parts = data[0].split('|');
                            if (parts.length === 3) {
                                const lat = parseFloat(parts[1]);
                                const lng = parseFloat(parts[2]);
                                
                                // Stocker les coordonnées dans les champs cachés
                                const latitudeField = document.querySelector('input[name="latitude"]');
                                const longitudeField = document.querySelector('input[name="longitude"]');
                                if (latitudeField && longitudeField) {
                                    latitudeField.value = lat;
                                    longitudeField.value = lng;
                                    console.log("Coordonnées GPS stockées:", lat, lng);
                                }
                                
                                // Ne pas essayer de zoomer ici, la carte n'existe pas encore
                                // La page de liste des établissements gérera le zoom
                            }
                        }
                        
                        // Soumettre le formulaire après avoir mis à jour les champs cachés
                        setTimeout(() => {
                            const form = document.querySelector('form');
                            if (form) {
                                console.log("Soumission du formulaire avec ville :", hiddenField.value);
                                console.log("Méthode du formulaire :", form.method);
                                form.submit();
                            } else {
                                console.error("Formulaire non trouvé !");
                            }
                        }, 100);
                    })
                    .catch(error => {
                        console.error("Erreur lors de la récupération des coordonnées GPS:", error);
                        // Soumettre le formulaire même en cas d'erreur
                        setTimeout(() => {
                            const form = document.querySelector('form');
                            if (form) {
                                form.submit();
                            }
                        }, 100);
                    });
            });
            resultsContainer.appendChild(div);
        });

        resultsContainer.classList.add("show");
        console.log("Results container should now be visible");
        console.log("Results container classes:", resultsContainer.className);
        console.log("Results container style:", resultsContainer.style.display);
    }

    /**
     * Récupère les villes correspondant à la requête depuis l'API.
     * @param {string} query - Terme de recherche pour les villes
     * @returns {Promise<Array<string>>} Liste des villes trouvées
     */
    async function fetchVilles(query) {
        console.log("fetchVilles called with query:", query);

        if (query.length < 2) {
            console.log("Query too short, hiding results");
            resultsContainer.classList.remove("show");
            return;
        }

        try {
            console.log("Fetching villes from API...");
            showLoading("Recherche en cours...");
            const response = await fetch(
                `/api/villes?q=${encodeURIComponent(query)}`,
            );
            console.log("API response status:", response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const villes = await response.json();
            console.log("API response data:", villes);
            hideLoading();
            showResults(villes);
        } catch (error) {
            console.error("Erreur lors de la récupération des villes:", error);
            hideLoading();
            resultsContainer.innerHTML = "";
            const errorDiv = document.createElement("div");
            errorDiv.className = "autocomplete-no-results";
            errorDiv.textContent = "Erreur de chargement: " + error.message;
            resultsContainer.appendChild(errorDiv);
            resultsContainer.classList.add("show");
        }
    }

    // Événement input avec débounce
    const debouncedFetch = debounce(fetchVilles);
    input.addEventListener("input", function (e) {
        console.log("Input event:", e.target.value);

        // Visual feedback for input
        input.style.backgroundColor = "#fffde7";
        setTimeout(() => {
            input.style.backgroundColor = "";
        }, 200);

        debouncedFetch(e.target.value);
    });

    // Synchroniser avec le champ caché lors de la saisie
    input.addEventListener("input", function (e) {
        console.log("Syncing with hidden field:", e.target.value);
        syncWithHiddenField();
    });

    // Synchroniser avec le champ caché lors de la sélection avec le clavier
    input.addEventListener("keydown", function (e) {
        console.log("Key down event:", e.key);
        if (e.key === "Enter") {
            console.log("Enter key pressed, syncing with hidden field");
            syncWithHiddenField();
        }
    });

    // Gestion du clic en dehors pour fermer les résultats
    document.addEventListener("click", function (e) {
        if (e.target !== input) {
            resultsContainer.classList.remove("show");
        }
    });

    console.log("Autocomplete fully initialized!");

    return true;
}

/**
 * Zoom vers la localisation spécifiée et met à jour le champ de ville
 * @param {number} lat - Latitude de la localisation
 * @param {number} lng - Longitude de la localisation
 * @param {string} villeName - Nom de la ville
 * @returns {void}
 */

/**
 * Initialise l'autocomplete Google Places pour la proposition d'établissements
 * @param {string} inputId - ID du champ de recherche
 * @param {string} apiKey - Clé API Google Maps
 * @returns {Promise<void>} Promesse résolue quand l'API est prête
 */
export function initGooglePlacesAutocomplete(inputId, apiKey) {
    return new Promise((resolve, reject) => {
        // Vérifier si l'API Google est déjà chargée
        if (typeof google === 'undefined' || !google.maps || !google.maps.places) {
            // Charger l'API Google Maps avec loading=async pour éviter les avertissements
            const script = document.createElement("script");
            script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=initGooglePlacesCallback&v=weekly&loading=async`;
            script.async = true;
            script.defer = true;
            script.onerror = () => reject(new Error("Failed to load Google Maps API"));
            document.head.appendChild(script);
            
            // Callback global pour l'initialisation
            window.initGooglePlacesCallback = () => {
                initializeAutocomplete(inputId, apiKey, resolve, reject);
            };
        } else {
            initializeAutocomplete(inputId, apiKey, resolve, reject);
        }
    });
}

/**
 * Initialise l'autocomplétion des lieux avec l'API Google Places
 * @param {string} inputId - ID du champ de recherche
 * @param {string} apiKey - Clé API Google Maps
 * @param {Function} resolve - Callback de résolution de la promesse
 * @param {Function} reject - Callback de rejet de la promesse
 * @returns {void}
 */
function initializeAutocomplete(inputId, apiKey, resolve, reject) {
    try {
        const input = document.getElementById(inputId);
        if (!input) {
            throw new Error(`Élément #${inputId} introuvable !`);
        }

        const autocomplete = new google.maps.places.Autocomplete(input, {
            types: ["bakery", "cafe", "restaurant", "bar", "food"],
            componentRestrictions: { country: "fr" },
        });

        autocomplete.addListener("place_changed", function () {
            console.log("=== DEBUT place_changed ===");
            const place = autocomplete.getPlace();
            console.log("Place object:", place);

            if (!place.geometry) {
                console.error(
                    "❌ Aucune information de géolocalisation disponible pour ce lieu.",
                );
                showToast("Aucune information de géolocalisation disponible pour ce lieu.", 'error');
                return;
            }

            console.log("✓ Géométrie disponible");
            console.log("Place ID:", place.place_id);
            console.log("Place name:", place.name);

            // Remplir les champs
            document.getElementById("ajout-etab-nom").value = place.name || "";
            document.getElementById("ajout-etab-adresse").value =
                place.formatted_address || "";
            document.getElementById("ajout-etab-latitude").value =
                place.geometry.location.lat();
            document.getElementById("ajout-etab-longitude").value =
                place.geometry.location.lng();
            document.getElementById("ajout-etab-google_place_id").value =
                place.place_id || "";

            // Vérification des champs après remplissage
            console.log(
                "Valeur du champ google_place_id après remplissage:",
                document.getElementById("ajout-etab-google_place_id").value,
            );
            console.log(
                "Longueur du google_place_id:",
                document.getElementById("ajout-etab-google_place_id").value.length,
            );

            // Vérification de tous les champs cachés
            console.log("Valeurs des champs cachés:");
            console.log("  nom:", document.getElementById("ajout-etab-nom").value);
            console.log(
                "  google_place_id:",
                document.getElementById("ajout-etab-google_place_id").value,
            );
            console.log(
                "  latitude:",
                document.getElementById("ajout-etab-latitude").value,
            );
            console.log(
                "  longitude:",
                document.getElementById("ajout-etab-longitude").value,
            );
            console.log("=== FIN place_changed ===");

            // Vérifier si le lieu est déjà dans la liste
            fetch("/verifier_etablissement", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector('meta[name="csrf-token"]')
                        .content,
                },
                body: JSON.stringify({ nom: place.name }),
            })
                .then(async (response) => {
                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(`Erreur serveur: ${errorText}`);
                    }
                    return response.json();
                })
                .then((data) => {
                    if (data.error) {
                        console.error("Erreur:", data.error);
                        showToast(data.error, 'error');
                        return;
                    }
                    if (data.exists) {
                        const etablissementUrl = data.url;
                        const etablissementId = data.id_etab;
                        console.log("Établissement existant, ID:", etablissementId);
                        const previousMessages =
                            document.querySelectorAll(".alert-warning");
                        previousMessages.forEach((msg) => msg.remove());
                        const message = document.createElement("div");
                        message.className = "alert alert-warning";
                        message.innerHTML = `Déjà présent : <a href="${data.url}">Voir la page</a>`;
                        document.querySelector(".form-container").prepend(message);
                        
                        // Désactiver le bouton de soumission pour empêcher l'ajout de doublon
                        const submitButton = document.querySelector('button[type="submit"]');
                        if (submitButton) {
                            submitButton.disabled = true;
                            submitButton.title = "Cet établissement existe déjà";
                        }
                    }
                    
                    // Appeler initMap ici, après avoir défini etablissementId
                    fetch("/extraire_infos_adresse", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]')
                                .content,
                        },
                        body: JSON.stringify({ adresse: place.formatted_address }),
                    })
                        .then((response) => response.json())
                        .then((data) => {
                            document.getElementById("ajout-etab-code_postal").value =
                                data.code_postal || "";
                            document.getElementById("ajout-etab-ville").value =
                                data.ville || "";
                            document.getElementById("ajout-etab-adresse").value =
                                data.adresse_nettoyee || "";
                            
                            // Initialiser la carte avec le marqueur de l'établissement
                            console.log("Appel de initMapWithMarker pour afficher l'établissement");
                            initMapWithMarker(
                                place.geometry.location.lat(),
                                place.geometry.location.lng(),
                                place.name
                            );
                        })
                        .catch((error) => {
                            console.error("Erreur:", error);
                            showToast(error.message, 'error');
                        });
                })
                .catch((error) => {
                    console.error("Erreur:", error);
                    showToast(error.message, 'error');
                });
        });

        resolve(autocomplete);
    } catch (error) {
        console.error("Erreur lors de l'initialisation de l'autocomplete:", error);
        showToast(error.message, 'error');
        reject(error);
    }
}

/**
 * Fonction pour zoomer sur une localisation spécifique sur la carte
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @param {string} villeName - Nom de la ville pour le marqueur
 */
export function zoomToLocation(lat, lng, villeName) {
    console.log("Zoom vers:", lat, lng, villeName);
    
    // Vérifier si la carte Google Maps existe
    if (typeof google !== 'undefined' && google.maps && window.map) {
        console.log("Zoom avec Google Maps");
        window.map.setCenter({lat: lat, lng: lng});
        window.map.setZoom(12);
        
        // Ajouter un marqueur
        if (window.marker) {
            window.marker.setMap(null);
        }
        window.marker = new google.maps.Marker({
            position: {lat: lat, lng: lng},
            map: window.map,
            title: villeName
        });
        
        // Si c'est une recherche d'établissements, on peut aussi centrer la recherche
        const searchForm = document.querySelector('form[action*="liste_etablissements"]');
        if (searchForm) {
            const latField = searchForm.querySelector('input[name="latitude"]');
            const lngField = searchForm.querySelector('input[name="longitude"]');
            if (latField && lngField) {
                latField.value = lat;
                lngField.value = lng;
            }
        }
    }
    // Vérifier si Leaflet est utilisé
    else if (typeof L !== 'undefined' && window.map) {
        console.log("Zoom avec Leaflet");
        window.map.setView([lat, lng], 12);
        
        // Ajouter un marqueur
        if (window.marker) {
            window.map.removeLayer(window.marker);
        }
        window.marker = L.marker([lat, lng]).addTo(window.map)
            .bindPopup(villeName)
            .openPopup();
    }
    // Si aucune carte n'est chargée, stocker les coordonnées pour plus tard
    else {
        console.log("Aucune carte détectée, stockage des coordonnées pour plus tard");
        window.pendingZoom = {lat: lat, lng: lng, ville: villeName};
    }
}

// Export pour compatibilité avec les anciens scripts
document.autocomplete = {
    initAutocomplete,
    initGooglePlacesAutocomplete,
    zoomToLocation
};
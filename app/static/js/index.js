/**
 * Initialise le système d'autocomplétion pour la recherche de villes.
 * Configure les événements et les fonctions nécessaires pour l'autocomplétion.
 * @returns {boolean} True si l'initialisation a réussi, false sinon
 */
function initAutocomplete() {
    const input = document.getElementById("ville-autocomplete");
    const resultsContainer = document.getElementById("autocomplete-results");
    let currentFocus = -1;

    if (!input || !resultsContainer) {
        console.log("Elements not found yet, waiting for DOM...");
        return false;
    }

    console.log("Elements found, initializing autocomplete");

    /**
     * Fonction de débounce pour limiter les appels fréquents.
     * @param {function} func - Fonction à exécuter
     * @param {number} timeout - Délai en millisecondes (par défaut: 300)
     * @returns {function} Fonction enveloppée avec débounce
     */
    function debounce(func, timeout = 300) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => {
                func.apply(this, args);
            }, timeout);
        };
    }

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
     * Affiche un indicateur de chargement pendant la recherche.
     */
    function showLoading() {
        resultsContainer.innerHTML = "";
        const loading = document.createElement("div");
        loading.className = "autocomplete-loading";
        loading.textContent = "Recherche en cours...";
        resultsContainer.appendChild(loading);
        resultsContainer.classList.add("show");
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
                
                // Soumettre le formulaire après avoir mis à jour le champ caché
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
            showLoading();
            const response = await fetch(
                `/api/villes?q=${encodeURIComponent(query)}`,
            );
            console.log("API response status:", response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const villes = await response.json();
            console.log("API response data:", villes);
            showResults(villes);
        } catch (error) {
            console.error("Erreur lors de la récupération des villes:", error);
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
 * Fonction utilitaire légère pour obtenir la position de l'utilisateur.
 * Ne nécessite pas Leaflet, utilise l'API de géolocalisation native.
 * @returns {Promise<object>} Objet contenant la latitude et la longitude
 */
function getUserLocationSimple() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error("La géolocalisation n'est pas supportée par votre navigateur"));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => resolve(position),
            (error) => reject(error),
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    });
}

/**
 * Initialise le bouton de géolocalisation et configure son comportement.
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
                const latitudeField = document.querySelector(
                    'input[name="latitude"]',
                );
                const longitudeField = document.querySelector(
                    'input[name="longitude"]',
                );

                if (latitudeField && longitudeField) {
                    latitudeField.value = position.coords.latitude;
                    longitudeField.value = position.coords.longitude;

                    // Construire l'URL avec les coordonnées et le flag de géolocalisation
                    const url = new URL(
                        window.location.origin +
                        '/liste_etablissements',
                    );
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

                alert(errorMessage);
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

// Initialisation
if (!initAutocomplete()) {
    // Fallback to DOMContentLoaded if elements not found
    console.log("Falling back to DOMContentLoaded...");
    document.addEventListener("DOMContentLoaded", initAutocomplete);
}

// Initialiser le bouton de géolocalisation
initGeolocButton();
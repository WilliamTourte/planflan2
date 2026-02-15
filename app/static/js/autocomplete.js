/**
 * Module d'autocomplete pour l'application PlanFlan
 * 
 * Ce module gère les fonctionnalités d'autocomplete pour les villes et les établissements
 */

import { debounce, showLoading, hideLoading, showToast } from './utils.js';

/**
 * Initialise le système d'autocomplétion pour la recherche de villes.
 * Configure les événements et les fonctions nécessaires pour l'autocomplétion.
 * @param {object} options - Options de configuration
 * @returns {boolean} True si l'initialisation a réussi, false sinon
 */
export function initAutocomplete(options = {}) {
    const input = document.getElementById("ville-autocomplete");
    let resultsContainer = document.getElementById("autocomplete-results");
    let currentFocus = -1;

    if (!input) {
        console.log("Input element not found, waiting for DOM...");
        return false;
    }

    // Détecter le type de page pour adapter le comportement
    const pageType = document.body.getAttribute('data-page-type');
    const isIndexPage = pageType === 'home';
    const isProposerPage = pageType === 'proposer_etablissement';

    // Si le conteneur des résultats n'existe pas, le créer
    if (!resultsContainer) {
        resultsContainer = document.createElement("div");
        resultsContainer.id = "autocomplete-results";
        resultsContainer.className = "autocomplete-results";
    }
    
    // Vérifier que le conteneur est bien dans le DOM
    if (!document.body.contains(resultsContainer)) {
        // Trouver le form-group parent pour un meilleur positionnement
        const formGroup = input.closest('.form-group');
        if (formGroup) {
            formGroup.appendChild(resultsContainer);
        } else {
            input.after(resultsContainer);
        }
    }

    // S'assurer que le parent a une position relative pour le positionnement absolu
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        const parentStyle = window.getComputedStyle(formGroup);
        if (parentStyle.position !== 'relative' && parentStyle.position !== 'absolute' && parentStyle.position !== 'fixed') {
            formGroup.style.position = 'relative';
        }
    }
    
    // Positionner le conteneur des résultats
    resultsContainer.style.position = 'absolute';
    resultsContainer.style.top = '100%';
    resultsContainer.style.left = '0';
    resultsContainer.style.right = '0';
    resultsContainer.style.zIndex = '10000';

    /**
     * Synchronise la valeur du champ de recherche avec le champ caché du formulaire.
     * Uniquement utilisé sur la page de proposition d'établissement.
     */
    function syncWithHiddenField() {
        // Sur la page d'accueil, pas besoin de synchronisation avec un champ caché
        if (isIndexPage) {
            return;
        }
        
        // Essayer plusieurs façons de trouver le champ ville
        let hiddenField = null;
        
        // 1. Essayer l'ID pour la page de proposition d'établissement
        hiddenField = document.getElementById('ajout-etab-ville');
        
        // 2. Si non trouvé, essayer le name pour la page d'accueil (compatibilité)
        if (!hiddenField) {
            hiddenField = document.querySelector('input[name="ville"]');
        }
        
        // 3. Essayer de trouver un champ qui contient "ville" dans son ID ou name
        if (!hiddenField) {
            const allInputs = document.querySelectorAll('input');
            for (let i = 0; i < allInputs.length; i++) {
                const inputEl = allInputs[i];
                if (inputEl.id && inputEl.id.toLowerCase().includes('ville')) {
                    hiddenField = inputEl;
                    break;
                }
                if (inputEl.name && inputEl.name.toLowerCase().includes('ville')) {
                    hiddenField = inputEl;
                    break;
                }
            }
        }
        
        if (hiddenField) {
            hiddenField.value = input.value;
        }
    }

    /**
     * Affiche les résultats de recherche des villes.
     * @param {Array<string>} villes - Liste des villes trouvées
     */
    function showResults(villes) {
        resultsContainer.innerHTML = "";
        
        // Forcer le positionnement et la visibilité
        resultsContainer.style.position = 'absolute';
        resultsContainer.style.zIndex = '10000';
        resultsContainer.style.width = '100%';
        resultsContainer.style.backgroundColor = 'white';
        resultsContainer.style.border = '1px solid #ddd';
        
        if (villes.length === 0) {
            const noResults = document.createElement("div");
            noResults.className = "autocomplete-no-results";
            noResults.textContent = "Aucun flan pour cette ville. \nProposer une adresse ?";
            resultsContainer.appendChild(noResults);
            resultsContainer.classList.add("show");
            

        }


        villes.forEach((ville) => {
            const div = document.createElement("div");
            div.className = "autocomplete-item";
            div.textContent = ville;
            
            // Style temporaire pour les éléments
            div.style.padding = '12px 15px';
            div.style.borderBottom = '1px solid #eee';
            div.style.backgroundColor = '#f8f9fa';
            
            div.addEventListener("click", function () {
                input.value = ville;
                
                // Essayer plusieurs façons de trouver le champ ville
                let hiddenField = null;
                
                // 1. Essayer l'ID pour la page de proposition d'établissement
                hiddenField = document.getElementById('ajout-etab-ville');
                
                // 2. Si non trouvé, essayer le name pour la page d'accueil
                if (!hiddenField) {
                    hiddenField = document.querySelector('input[name="ville"]');
                }
                
                // 3. Essayer de trouver un champ qui contient "ville" dans son ID ou name
                if (!hiddenField) {
                    const allInputs = document.querySelectorAll('input');
                    for (let i = 0; i < allInputs.length; i++) {
                        const inputEl = allInputs[i];
                        if (inputEl.id && inputEl.id.toLowerCase().includes('ville')) {
                            hiddenField = inputEl;
                            break;
                        }
                        if (inputEl.name && inputEl.name.toLowerCase().includes('ville')) {
                            hiddenField = inputEl;
                            break;
                        }
                    }
                }
                
                if (hiddenField) {
                    hiddenField.value = ville;
                }
                resultsContainer.classList.remove("show");
                
                // Déclencher un événement personnalisé pour indiquer qu'une ville a été sélectionnée
                const villeSelectedEvent = new CustomEvent('villeSelected', {
                    detail: { ville: ville },
                    bubbles: true
                });
                input.dispatchEvent(villeSelectedEvent);
                
                // Masquer les résultats après sélection
                resultsContainer.classList.remove("show");
                
                // Comportement différent selon la page
                if (isIndexPage) {
                    // Récupérer les coordonnées GPS pour zoomer sur la carte
                    fetch(`/api/villes?q=${encodeURIComponent(ville)}&with_gps=true`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.length > 0) {
                                const parts = data[0].split('|');
                                if (parts.length === 3) {
                                    const lat = parseFloat(parts[1]);
                                    const lng = parseFloat(parts[2]);
                                    
                                    // Rediriger vers la page de liste avec les coordonnées
                                    const url = new URL(window.location.origin + '/liste_etablissements');
                                    url.searchParams.append("ville", ville);
                                    url.searchParams.append("latitude", lat);
                                    url.searchParams.append("longitude", lng);
                                    url.searchParams.append("from_ville_selection", "true");
                                    
                                    window.location.href = url.toString();
                                    return;
                                }
                            }
                            
                            // Si pas de coordonnées trouvées, soumettre le formulaire normalement
                            const form = document.querySelector('form');
                            if (form) {
                                form.submit();
                            }
                        })
                        .catch(error => {
                            console.error("Erreur lors de la récupération des coordonnées GPS:", error);
                            // Soumettre le formulaire en cas d'erreur
                            const form = document.querySelector('form');
                            if (form) {
                                form.submit();
                            }
                        });
                } else if (isProposerPage) {
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
                                    }
                                }
                            }
                        })
                        .catch(error => {
                            console.error("Erreur lors de la récupération des coordonnées GPS:", error);
                        });
                }
            });
            resultsContainer.appendChild(div);
        });

        resultsContainer.classList.add("show");
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

    // Synchroniser avec le champ caché lors de la saisie (uniquement sur la page de proposition)
    if (!isIndexPage) {
        input.addEventListener("input", function (e) {
            syncWithHiddenField();
        });
    }

    // Synchroniser avec le champ caché lors de la sélection avec le clavier (uniquement sur la page de proposition)
    if (!isIndexPage) {
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                syncWithHiddenField();
            }
        });
    }

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
 * Recherche des établissements dans une ville spécifique en utilisant d'abord l'API locale
 * @param {string} ville - Nom de la ville
 * @param {string} query - Terme de recherche pour les établissements
 * @returns {Promise<Array>} Promesse résolue avec la liste des établissements
 */
export function searchEtablissementsByVille(ville, query = "") {
    return new Promise((resolve, reject) => {
        // D'abord, essayer de trouver des établissements dans notre base de données
        fetch(`/api/etablissements?ville=${encodeURIComponent(ville)}&q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur serveur: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Si nous avons des résultats locaux, les retourner
                if (data && data.length > 0) {
                    resolve(data);
                } else {
                    // Sinon, utiliser Google Places comme fallback
                    if (typeof google !== 'undefined' && google.maps && google.maps.places) {
                        const service = new google.maps.places.PlacesService(document.createElement('div'));
                        
                        service.textSearch({
                            query: `${query} ${ville}`,
                            type: 'bakery',
                            location: new google.maps.LatLng(48.8566, 2.3522), // Paris par défaut
                            radius: 50000 // 50km autour du centre
                        }, (results, status) => {
                            if (status === google.maps.places.PlacesServiceStatus.OK) {
                                resolve(results);
                            } else {
                                reject(new Error(`Erreur de recherche Google: ${status}`));
                            }
                        });
                    } else {
                        reject(new Error("Google Maps API not loaded"));
                    }
                }
            })
            .catch(error => {
                console.error("Erreur lors de la recherche locale:", error);
                reject(error);
            });
    });
}

/**
 * Affiche les résultats de recherche des établissements dans une liste personnalisée
 * @param {Array} etablissements - Liste des établissements
 * @param {string} inputId - ID du champ de recherche
 */
function showEtablissementResults(etablissements, inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;

    // Créer ou trouver le conteneur des résultats
    let resultsContainer = document.getElementById(`${inputId}-results`);
    if (!resultsContainer) {
        resultsContainer = document.createElement('div');
        resultsContainer.id = `${inputId}-results`;
        resultsContainer.className = 'etablissement-autocomplete-results';
        input.parentNode.insertBefore(resultsContainer, input.nextSibling);
    }

    // Effacer les résultats précédents
    resultsContainer.innerHTML = '';

    if (!etablissements || etablissements.length === 0) {
        resultsContainer.style.display = 'none';
        return;
    }

    // Afficher les nouveaux résultats
    etablissements.forEach(etab => {
        const div = document.createElement('div');
        div.className = 'etablissement-autocomplete-item';
        
        // Extraire les informations de l'établissement
        const name = etab.name || etab.nom || 'Établissement inconnu';
        const address = etab.formatted_address || etab.adresse || etab.ville || '';
        
        div.innerHTML = `
            <strong>${name}</strong>
            <div class="etablissement-address">${address}</div>
        `;

        div.addEventListener('click', function() {
            // Remplir les champs avec les informations de l'établissement sélectionné
            document.getElementById('ajout-etab-nom').value = name;
            
            if (etab.formatted_address) {
                document.getElementById('ajout-etab-adresse').value = etab.formatted_address;
            } else if (etab.adresse) {
                document.getElementById('ajout-etab-adresse').value = etab.adresse;
            }

            if (etab.geometry && etab.geometry.location) {
                document.getElementById('ajout-etab-latitude').value = etab.geometry.location.lat();
                document.getElementById('ajout-etab-longitude').value = etab.geometry.location.lng();
            } else if (etab.latitude && etab.longitude) {
                document.getElementById('ajout-etab-latitude').value = etab.latitude;
                document.getElementById('ajout-etab-longitude').value = etab.longitude;
            }

            if (etab.place_id) {
                document.getElementById('ajout-etab-google_place_id').value = etab.place_id;
            }

            // Masquer les résultats après sélection
            resultsContainer.style.display = 'none';
        });

        resultsContainer.appendChild(div);
    });

    resultsContainer.style.display = 'block';
}

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

        // Utiliser l'autocomplete standard Google Places (sans logique de ville)
        setupGooglePlacesAutocomplete(input, apiKey, resolve, reject);
    } catch (error) {
        console.error("Erreur lors de l'initialisation de l'autocomplete:", error);
        showToast(error.message, 'error');
        reject(error);
    }
}

/**
 * Initialise Google Places Autocomplete avec restriction à une ville spécifique (par nom)
 * @param {string} inputId - ID du champ de recherche
 * @param {string} apiKey - Clé API Google Maps
 * @param {string} villeName - Nom de la ville pour la restriction
 * @returns {Promise<void>}
 */
export function initGooglePlacesAutocompleteWithCity(inputId, apiKey, villeName) {
    return new Promise((resolve, reject) => {

        
        // Si aucune ville n'est spécifiée, utiliser l'initialisation standard
        if (!villeName) {

            return initGooglePlacesAutocomplete(inputId, apiKey).then(resolve).catch(reject);
        }
        
        // Nettoyer toute instance précédente d'autocomplete
        const input = document.getElementById(inputId);
        if (input) {
            // Supprimer tous les écouteurs d'événements précédents
            const newInput = input.cloneNode(true);
            input.parentNode.replaceChild(newInput, input);
        }


        // Obtenir les coordonnées GPS de la ville (uniquement pour la restriction)
        fetch(`/api/villes?q=${encodeURIComponent(villeName)}&with_gps=true`)
            .then(response => {

                return response.json();
            })
            .then(data => {

                if (data.length > 0) {
                    const parts = data[0].split('|');

                    if (parts.length === 3) {
                        const lat = parseFloat(parts[1]);
                        const lng = parseFloat(parts[2]);


                        // Initialiser avec restriction géographique (mais nous n'affichons pas les coordonnées)
                        setupAutocompleteWithCityRestriction(inputId, apiKey, lat, lng, villeName, resolve, reject);
                        return;
                    }
                }

                // Si on ne trouve pas les coordonnées, utiliser l'initialisation standard
                initGooglePlacesAutocomplete(inputId, apiKey).then(resolve).catch(reject);
            })
            .catch(error => {

                initGooglePlacesAutocomplete(inputId, apiKey).then(resolve).catch(reject);
            });
    });
}

/**
 * Configure l'autocomplete avec restriction à une ville (les coordonnées sont utilisées uniquement pour la restriction)
 */
function setupAutocompleteWithCityRestriction(inputId, apiKey, lat, lng, villeName, resolve, reject) {
    try {
        const input = document.getElementById(inputId);
        if (!input) {
            throw new Error(`Élément #${inputId} introuvable !`);
        }

        // Vérifier si l'API Google est déjà chargée
        if (typeof google === 'undefined' || !google.maps || !google.maps.places) {
            // Charger l'API Google Maps
            const script = document.createElement("script");
            script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=initPlacesWithCityCallback&v=weekly&loading=async`;
            script.async = true;
            script.defer = true;
            script.onerror = () => reject(new Error("Failed to load Google Maps API"));
            document.head.appendChild(script);

            // Callback global
            window.initPlacesWithCityCallback = () => {

                initializeAutocompleteWithCity(input, apiKey, lat, lng, villeName, resolve, reject);
            };
        } else {

            initializeAutocompleteWithCity(input, apiKey, lat, lng, villeName, resolve, reject);
        }
    } catch (error) {

        showToast(error.message, 'error');
        reject(error);
    }
}

/**
 * Calcule la distance entre deux points géographiques en kilomètres
 * (version JavaScript de la fonction Python calculer_distance)
 */
function calculerDistance(lat1, lon1, lat2, lon2) {
    const earthRadius = 6371.0;
    // Convertir toutes les valeurs en float puis en radians
    lat1 = parseFloat(lat1);
    lon1 = parseFloat(lon1);
    lat2 = parseFloat(lat2);
    lon2 = parseFloat(lon2);
    
    const lat1Rad = lat1 * Math.PI / 180;
    const lon1Rad = lon1 * Math.PI / 180;
    const lat2Rad = lat2 * Math.PI / 180;
    const lon2Rad = lon2 * Math.PI / 180;
    
    const dlat = lat2Rad - lat1Rad;
    const dlon = lon2Rad - lon1Rad;
    const a = Math.sin(dlat / 2) ** 2 + Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.sin(dlon / 2) ** 2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return earthRadius * c;
}

/**
 * Initialise l'autocomplete avec restriction à une ville spécifique
 */
function initializeAutocompleteWithCity(input, apiKey, lat, lng, villeName, resolve, reject) {
    try {

        
        const center = new google.maps.LatLng(lat, lng);
        console.log("DEBUG: Centre créé:", center);

        // Calculer les bounds pour une zone de 10km autour de la ville
        const earthRadius = 6371.0; // Rayon de la Terre en km
        const radiusKm = 10; // Rayon de recherche de 10km
        
        // Convertir la distance en degrés de latitude/longitude
        const latRadius = radiusKm / earthRadius * (180 / Math.PI);
        const lngRadius = latRadius / Math.cos(lat * Math.PI / 180);
        
        const bounds = new google.maps.LatLngBounds(
            new google.maps.LatLng(lat - latRadius, lng - lngRadius),
            new google.maps.LatLng(lat + latRadius, lng + lngRadius)
        );

        // Utiliser Autocomplete avec des paramètres améliorés
        const autocomplete = new google.maps.places.Autocomplete(input, {
            types: ["bakery", "cafe", "restaurant", "bar", "food"],
            componentRestrictions: { country: "fr" },
            // Utiliser strictBounds pour une restriction stricte
            strictBounds: true,
            // Définir les bounds calculés
            bounds: bounds,
            // Ajouter aussi un bias pour améliorer les résultats
            location: center,
            radius: 10000 // 10km
        });

        console.log("DEBUG: Autocomplete créé avec les options:", {
            types: ["bakery", "cafe", "restaurant", "bar", "food"],
            componentRestrictions: { country: "fr" },
            strictBounds: true,
            bounds: bounds,
            location: {lat: lat, lng: lng},
            radius: 10000
        });

        // Stocker les informations pour le filtre côté client
        autocomplete.cityName = villeName;
        autocomplete.cityLat = lat;
        autocomplete.cityLng = lng;
        autocomplete.cityBounds = bounds;

        // Ajouter un écouteur pour filtrer les prédictions en temps réel
        autocomplete.addListener("place_changed", function () {
            console.log("DEBUG: Événement place_changed déclenché");
            const place = autocomplete.getPlace();
            console.log("DEBUG: Place sélectionnée:", place);

            if (!place.geometry) {
                console.error("❌ Aucune information de géolocalisation disponible pour ce lieu.");
                showToast("Aucune information de géolocalisation disponible pour ce lieu.", 'error');
                return;
            }

            // Vérification stricte côté client : le lieu doit être dans les bounds
            const placeLat = place.geometry.location.lat();
            const placeLng = place.geometry.location.lng();
            const placeLocation = new google.maps.LatLng(placeLat, placeLng);
            
            // Vérifier si le lieu est dans les bounds
            const isInBounds = bounds.contains(placeLocation);



            if (!isInBounds) {
                // Calculer la distance pour le message
                const distance = calculerDistance(lat, lng, placeLat, placeLng);
                console.warn("⚠️ Le lieu sélectionné est en dehors de la zone de " + villeName + " (distance:", distance.toFixed(2), "km)");
                showToast("Ce lieu est en dehors de la zone de " + villeName + " (" + distance.toFixed(1) + "km). Veuillez choisir un établissement dans la ville sélectionnée.", 'warning');
                // Réinitialiser le champ de recherche
                input.value = '';
                return;
            }

            console.log("DEBUG: Géométrie valide et dans les bounds, remplissage des champs");
            // Remplir les champs (comme avant)
            document.getElementById("ajout-etab-nom").value = place.name || "";
            document.getElementById("ajout-etab-adresse").value = place.formatted_address || "";
            document.getElementById("ajout-etab-latitude").value = place.geometry.location.lat();
            document.getElementById("ajout-etab-longitude").value = place.geometry.location.lng();
            document.getElementById("ajout-etab-google_place_id").value = place.place_id || "";

            // Extraire le nom de la ville des address_components
            let foundVilleName = "";
            if (place.address_components) {
                const cityComponent = place.address_components.find(component =>
                    component.types.includes("locality")
                );
                if (cityComponent) {
                    foundVilleName = cityComponent.long_name;
                }
            }

            // Remplir le champ ville si trouvé
            if (foundVilleName && document.getElementById("ajout-etab-ville")) {
                document.getElementById("ajout-etab-ville").value = foundVilleName;
            }

            // Vérifier si le lieu est déjà dans la liste
            window.verifyAndProcessEtablissement(place);
        });


        
        // Ajouter un feedback visuel pour montrer la zone de recherche
        const villeInput = document.getElementById('ville-autocomplete');
        if (villeInput) {
            const feedbackElement = document.createElement('div');
            feedbackElement.className = 'autocomplete-city-feedback';
            feedbackElement.textContent = `Recherche limitée à ${villeName} et ses environs (10km)`;
            
            // Insérer après le champ de recherche d'établissement
            const searchInput = document.getElementById('search');
            if (searchInput) {
                searchInput.parentNode.insertBefore(feedbackElement, searchInput.nextSibling);
            }
        }
        
        resolve(autocomplete);
    } catch (error) {
        console.error("DEBUG: Erreur lors de la configuration de l'autocomplete:", error);
        showToast(error.message, 'error');
        reject(error);
    }
}

/**
 * Nettoie le feedback visuel de restriction de ville
 */
export function clearCityRestrictionFeedback() {
    const feedbackElement = document.querySelector('.autocomplete-city-feedback');
    if (feedbackElement) {
        feedbackElement.remove();
    }
}

/**
 * Configure l'autocomplete personnalisé pour une ville spécifique
 * (Cette fonction n'est plus utilisée mais est conservée pour compatibilité)
 */
function setupCustomAutocomplete(input, inputId, villeName) {
    console.warn("setupCustomAutocomplete est dépréciée et n'est plus utilisée");
    // Utiliser l'autocomplete standard Google Places à la place
    if (typeof google !== 'undefined' && google.maps && google.maps.places) {
        const autocomplete = new google.maps.places.Autocomplete(input, {
            types: ["bakery", "cafe", "restaurant", "bar", "food"],
            componentRestrictions: { country: "fr" },
        });
        
        autocomplete.addListener("place_changed", function () {
            const place = autocomplete.getPlace();
            if (!place.geometry) {
                console.error("❌ Aucune information de géolocalisation disponible pour ce lieu.");
                showToast("Aucune information de géolocalisation disponible pour ce lieu.", 'error');
                return;
            }
            
            // Remplir les champs
            document.getElementById("ajout-etab-nom").value = place.name || "";
            document.getElementById("ajout-etab-adresse").value = place.formatted_address || "";
            document.getElementById("ajout-etab-latitude").value = place.geometry.location.lat();
            document.getElementById("ajout-etab-longitude").value = place.geometry.location.lng();
            document.getElementById("ajout-etab-google_place_id").value = place.place_id || "";
            
            // Extraire le nom de la ville des address_components
            let villeName = "";
            if (place.address_components) {
                const cityComponent = place.address_components.find(component =>
                    component.types.includes("locality")
                );
                if (cityComponent) {
                    villeName = cityComponent.long_name;
                }
            }
            
            // Remplir le champ ville si trouvé
            if (villeName && document.getElementById("ajout-etab-ville")) {
                document.getElementById("ajout-etab-ville").value = villeName;
            }
            
            // Vérifier si le lieu est déjà dans la liste
            window.verifyAndProcessEtablissement(place);
        });
    }
}

/**
 * Configure l'autocomplete Google Places standard
 */
function setupGooglePlacesAutocomplete(input, apiKey, resolve, reject) {
    try {
        const autocomplete = new google.maps.places.Autocomplete(input, {
            types: ["bakery", "cafe", "restaurant", "bar", "food"],
            componentRestrictions: { country: "fr" },
        });

        autocomplete.addListener("place_changed", function () {
            const place = autocomplete.getPlace();

            if (!place.geometry) {
                console.error("❌ Aucune information de géolocalisation disponible pour ce lieu.");
                showToast("Aucune information de géolocalisation disponible pour ce lieu.", 'error');
                return;
            }

            // Extraire le nom de la ville des address_components
            let villeName = "";
            if (place.address_components) {
                const cityComponent = place.address_components.find(component =>
                    component.types.includes("locality")
                );
                if (cityComponent) {
                    villeName = cityComponent.long_name;
                }
            }

            // Remplir les champs
            document.getElementById("ajout-etab-nom").value = place.name || "";
            document.getElementById("ajout-etab-adresse").value = place.formatted_address || "";
            document.getElementById("ajout-etab-latitude").value = place.geometry.location.lat();
            document.getElementById("ajout-etab-longitude").value = place.geometry.location.lng();
            document.getElementById("ajout-etab-google_place_id").value = place.place_id || "";

            // Remplir le champ ville si trouvé
            if (villeName && document.getElementById("ajout-etab-ville")) {
                document.getElementById("ajout-etab-ville").value = villeName;
            }

            // Vérifier si le lieu est déjà dans la liste
            window.verifyAndProcessEtablissement(place);
        });

        resolve(autocomplete);
    } catch (error) {
        console.error("Erreur lors de la configuration de Google Places Autocomplete:", error);
        showToast(error.message, 'error');
        reject(error);
    }
}

/**
 * Vérifie si l'établissement existe et traite les données
 */
// Définir la fonction sur l'objet window pour qu'elle soit mockable dans les tests
window.verifyAndProcessEtablissement = function verifyAndProcessEtablissement(place) {
    fetch("/verifier_etablissement", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
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
            // Retourner une promesse résolue pour éviter les erreurs de chaîne
            return Promise.resolve(null);
        }
        
        if (data.exists) {
            handleExistingEtablissement(data);
        }
        
        // Extraire les informations de l'adresse
        return extractAddressInfo(place.formatted_address);
    })
    .then((data) => {
        if (data) {
            document.getElementById("ajout-etab-code_postal").value = data.code_postal || "";
            document.getElementById("ajout-etab-ville").value = data.ville || "";
            document.getElementById("ajout-etab-adresse").value = data.adresse_nettoyee || "";
            
            // Initialiser la carte avec le marqueur de l'établissement
            // Utiliser setTimeout pour éviter les problèmes de timing
            setTimeout(() => {
                try {
                    // Vérifier que la fonction est disponible dans le scope global
                    if (typeof window.initMapWithInfowindow === 'function') {
                        // Vérifier aussi que la carte est prête avant d'appeler
                        if (window.map && window.map.addLayer && typeof window.map.addLayer === 'function') {
                            window.initMapWithInfowindow(); // Appeler la fonction globale
                        } else {
                            console.warn("La carte n'est pas encore prête, initialisation reportée");
                            // Réessayer après un délai plus long
                            setTimeout(() => {
                                if (typeof window.initMapWithInfowindow === 'function') {
                                    window.initMapWithInfowindow();
                                }
                            }, 500);
                        }
                    } else {
                        console.error("La fonction initMapWithInfowindow n'est pas disponible");
                        showToast("Erreur d'initialisation de la carte", 'error');
                    }
                } catch (e) {
                    console.error("Erreur détaillée lors de l'initialisation de la carte:", e);
                    showToast("Erreur carte: " + e.message, 'error');
                }
            }, 100);
        }
    })
    .catch((error) => {
        console.error("Erreur:", error);
        showToast(error.message, 'error');
        // Retourner une promesse résolue pour éviter les erreurs non capturées
        return Promise.resolve();
    });
}

/**
 * Gère le cas où l'établissement existe déjà
 */
function handleExistingEtablissement(data) {
    const etablissementUrl = data.url;
    const etablissementId = data.id_etab;
    console.log("Établissement existant, ID:", etablissementId);
    const previousMessages = document.querySelectorAll(".alert-warning");
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

/**
 * Extrait les informations de l'adresse
 */
function extractAddressInfo(adresse) {
    return fetch("/extraire_infos_adresse", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
        },
        body: JSON.stringify({ adresse: adresse }),
    })
    .then((response) => response.json());
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

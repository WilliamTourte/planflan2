let autocomplete;
let map;
let etablissementUrl = null;
let etablissementId = null;

window.initAutocomplete = function () {
    const input = document.getElementById("search");
    if (!input) {
        console.error("Élément #search introuvable !");
        return;
    }
    autocomplete = new google.maps.places.Autocomplete(input, {
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
                    return;
                }
                if (data.exists) {
                    etablissementUrl = data.url;
                    etablissementId = data.id_etab;
                    console.log("Établissement existant, ID:", etablissementId);
                    const previousMessages =
                        document.querySelectorAll(".alert-warning");
                    previousMessages.forEach((msg) => msg.remove());
                    const message = document.createElement("div");
                    message.className = "alert alert-warning";
                    message.innerHTML = `Déjà présent : <a href="${data.url}">Voir la page</a>`;
                    document.querySelector(".form-container").prepend(message);
                } else {
                    etablissementUrl = null;
                    etablissementId = null;
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
                        initMap(
                            place.geometry.location.lat(),
                            place.geometry.location.lng(),
                            place.name,
                        );
                    })
                    .catch((error) => console.error("Erreur:", error));
            })
            .catch((error) => {
                console.error("Erreur:", error);
                const errorMessage = document.createElement("div");
                errorMessage.className = "alert alert-danger";
                errorMessage.textContent = `Erreur: ${error.message}`;
                document.querySelector(".form-container").prepend(errorMessage);
                etablissementUrl = null;
                etablissementId = null;
            });
    });
};

window.initMap = function (lat, lng, title) {
    const mapElement = document.getElementById("map");
    if (!mapElement) {
        console.error("Élément #map introuvable !");
        const mapContainer = document.getElementById("map");
        if (mapContainer)
            mapContainer.innerHTML =
                "<p style='color: red;'>Erreur : Impossible de charger la carte.</p>";
        return;
    }
    const mapContainer = document.getElementById("map");
    mapContainer.style.display = "block";

    // Si une carte existe déjà, la détruire avant d'en créer une nouvelle
    if (map) {
        map.remove();
    }

    let center = [46.2276, 2.2137];
    let zoom = 6;
    if (lat && lng) {
        center = [lat, lng];
        zoom = 15;
    }
    map = L.map("map").setView(center, zoom);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // Si on a un établissement sélectionné via l'autocomplete
    if (lat && lng && title) {
        const marker = L.marker([lat, lng]).addTo(map);
        if (etablissementId) {
            marker.bindPopup("Chargement en cours...").openPopup();
            fetch(`/get_infowindow_content?id_etab=${etablissementId}`)
                .then((response) => response.text())
                .then((content) => {
                    marker.setPopupContent(content);
                })
                .catch((error) => {
                    console.error("Erreur lors du chargement de l'infowindow:", error);
                    let popupContent = `<b>${title}</b>`;
                    if (etablissementUrl) {
                        popupContent += `<br><a href="${etablissementUrl}" target="_blank">Voir la page de l'établissement</a>`;
                    }
                    marker.setPopupContent(popupContent);
                });
        } else {
            let popupContent = `<b>${title}</b>`;
            if (etablissementUrl) {
                popupContent += `<br><a href="${etablissementUrl}" target="_blank">Voir la page de l'établissement</a>`;
            }
            marker.bindPopup(popupContent).openPopup();
        }
    }
};

document.addEventListener("DOMContentLoaded", function () {
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${window.googleMapsApiKey}&libraries=places&callback=initAutocomplete&v=weekly&loading=async`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
});

// Gestion de la soumission du formulaire
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (e) {
            console.log("=== SOUMISSION DU FORMULAIRE ===");
            console.log(
                "Valeur de google_place_id avant soumission:",
                document.getElementById("ajout-etab-google_place_id").value,
            );

            // Vérifier tous les champs cachés
            const hiddenFields = document.querySelectorAll(
                ".etablissement-hidden-fields input",
            );
            console.log("Champs cachés dans le formulaire:");
            hiddenFields.forEach((field) => {
                console.log(
                    `  ${field.name}: ${field.value} (type: ${field.type})`,
                );
            });
            console.log("=== FIN SOUMISSION ===");
        });
    }
});
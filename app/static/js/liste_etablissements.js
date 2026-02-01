document.addEventListener('DOMContentLoaded', function() {
    const etablissementsData = JSON.parse(document.getElementById('etablissements-data').getAttribute('data-etablissements'));
    const isAdmin = JSON.parse(document.getElementById('is-admin').getAttribute('data-is-admin'));
    const googleMapsApiKey = document.getElementById('google-maps-api-key').getAttribute('data-api-key');

    // Ajout des coordonnées utilisateur si disponibles
    const userLocationElement = document.getElementById('user-location');
    const userLat = userLocationElement ? parseFloat(userLocationElement.getAttribute('data-lat')) : null;
    const userLon = userLocationElement ? parseFloat(userLocationElement.getAttribute('data-lon')) : null;

    // Ajout de la ville sélectionnée si disponible
    const villeSelectionneeElement = document.getElementById('ville-selectionnee');
    const villeSelectionnee = villeSelectionneeElement ? villeSelectionneeElement.getAttribute('data-ville') : null;

    // Initialiser la carte et les filtres
    if (typeof initMapAndFilters === 'function') {
        initMapAndFilters(etablissementsData, isAdmin, googleMapsApiKey, userLat, userLon, villeSelectionnee);
    }
});
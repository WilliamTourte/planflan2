// Fonction pour gérer le retour avec fallback
function goBackOrRedirect(fallbackUrl) {
    // Solution simple : utiliser le referrer pour décider
    var referrer = document.referrer;
    
    // Si nous venons d'une page du même site, essayer de revenir en arrière
    if (referrer && referrer.includes(window.location.host)) {
        try {
            window.history.back();
        } catch (e) {
            window.location.href = fallbackUrl;
        }
    } else {
        // Si nous sommes arrivés directement (pas de referrer ou referrer externe),
        // utiliser le fallback
        window.location.href = fallbackUrl;
    }
}

// Logique pour alterner entre recherche simple et complexe
document.addEventListener('DOMContentLoaded', function() {
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
});
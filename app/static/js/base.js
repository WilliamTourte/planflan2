/**
 * Function to handle navigation with fallback.
 * Attempts to go back in history, falls back to specified URL if not possible.
 * @param {string} fallbackUrl - The URL to fall back to if history navigation fails
 */
export function goBackOrRedirect(fallbackUrl) {
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

// Ajouter la fonction au scope global pour compatibilité avec les scripts inline
window.goBackOrRedirect = goBackOrRedirect;


/**
 * Fonction de débounce pour limiter les appels fréquents.
 * @param {Function} func - Fonction à exécuter
 * @param {number} timeout - Délai en millisecondes (par défaut: 300)
 * @returns {Function} Fonction enveloppée avec débounce
 */
export function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => {
            func.apply(this, args);
        }, timeout);
    };
}

/**
 * Initialise l'autocomplétion pour la barre de recherche du header.
 * Permet de rechercher des établissements par nom ou ville.
 */
export function initHeaderAutocomplete() {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('header-autocomplete-results');
    const searchForm = document.getElementById('header-search-form');

    if (!searchInput || !resultsContainer) {
        return false;
    }

    let currentFocus = -1;
    let lastResults = [];

    /**
     * Affiche un indicateur de chargement.
     */
    function showLoading() {
        resultsContainer.innerHTML = '';
        const loading = document.createElement('div');
        loading.className = 'autocomplete-loading';
        loading.textContent = 'Recherche en cours...';
        resultsContainer.appendChild(loading);
        resultsContainer.classList.add('show');
    }

    /**
     * Affiche les résultats de recherche.
     * @param {Array} etablissements - Liste des établissements trouvés
     */
    function showResults(etablissements) {
        resultsContainer.innerHTML = '';
        lastResults = etablissements;
        currentFocus = -1;

        if (etablissements.length === 0) {
            const noResults = document.createElement('div');
            noResults.className = 'autocomplete-no-results';
            noResults.textContent = 'Aucun établissement trouvé';
            resultsContainer.appendChild(noResults);
            resultsContainer.classList.add('show');
            return;
        }

        etablissements.forEach((etab, index) => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.innerHTML = `<strong>${etab.nom}</strong> <span class="text-muted">- ${etab.ville}</span>`;
            div.dataset.index = index;
            div.dataset.url = etab.url;
            div.dataset.id = etab.id_etab;

            div.addEventListener('click', function() {
                window.location.href = etab.url;
            });

            div.addEventListener('mouseenter', function() {
                removeActive();
                currentFocus = index;
                div.classList.add('active');
            });

            resultsContainer.appendChild(div);
        });

        resultsContainer.classList.add('show');
    }

    /**
     * Masque les résultats.
     */
    function hideResults() {
        resultsContainer.classList.remove('show');
        currentFocus = -1;
    }

    /**
     * Retire la classe active de tous les éléments.
     */
    function removeActive() {
        const items = resultsContainer.querySelectorAll('.autocomplete-item');
        items.forEach(item => item.classList.remove('active'));
    }

    /**
     * Ajoute la classe active à l'élément courant.
     */
    function addActive() {
        const items = resultsContainer.querySelectorAll('.autocomplete-item');
        if (items.length === 0) return;

        removeActive();

        if (currentFocus >= items.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = items.length - 1;

        items[currentFocus].classList.add('active');
        items[currentFocus].scrollIntoView({ block: 'nearest' });
    }

    /**
     * Récupère les établissements correspondant à la requête.
     * @param {string} query - Terme de recherche
     */
    async function fetchEtablissements(query) {
        if (query.length < 2) {
            hideResults();
            return;
        }

        try {
            showLoading();
            const response = await fetch(`/api/etablissements/search?q=${encodeURIComponent(query)}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const etablissements = await response.json();
            showResults(etablissements);
        } catch (error) {
            console.error('Erreur lors de la recherche:', error);
            resultsContainer.innerHTML = '';
            const errorDiv = document.createElement('div');
            errorDiv.className = 'autocomplete-no-results';
            errorDiv.textContent = 'Erreur de chargement';
            resultsContainer.appendChild(errorDiv);
            resultsContainer.classList.add('show');
        }
    }

    // Événement input avec débounce
    const debouncedFetch = debounce(fetchEtablissements);
    searchInput.addEventListener('input', function(e) {
        debouncedFetch(e.target.value.trim());
    });

    // Navigation au clavier
    searchInput.addEventListener('keydown', function(e) {
        const items = resultsContainer.querySelectorAll('.autocomplete-item');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            currentFocus++;
            addActive();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            currentFocus--;
            addActive();
        } else if (e.key === 'Enter') {
            if (currentFocus > -1 && items[currentFocus]) {
                e.preventDefault();
                window.location.href = items[currentFocus].dataset.url;
            }
            // Si aucun élément sélectionné, laisser le formulaire se soumettre normalement
        } else if (e.key === 'Escape') {
            hideResults();
            searchInput.blur();
        }
    });

    // Fermer les résultats au clic en dehors
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
            hideResults();
        }
    });

    // Gestion de la soumission du formulaire
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const query = searchInput.value.trim();

            // Si le champ est vide, rediriger vers la page de recherche avancée
            if (query === '') {
                e.preventDefault();
                window.location.href = '/rechercher';
                return;
            }

            // Si un seul résultat, rediriger directement vers l'établissement
            if (lastResults.length === 1) {
                e.preventDefault();
                window.location.href = lastResults[0].url;
                return;
            }

            // Sinon, laisser le formulaire se soumettre normalement vers liste_etablissements
        });
    }

    return true;
}


// Logique pour alterner entre recherche simple et complexe
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser l'autocomplete du header
    initHeaderAutocomplete();

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


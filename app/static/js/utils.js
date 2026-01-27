/**
 * Module utilitaire pour les fonctions communes
 * 
 * Ce module contient des fonctions utilitaires réutilisables dans toute l'application
 */

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
 * Affiche un indicateur de chargement.
 * @param {string} message - Message à afficher (par défaut: "Chargement...")
 * @returns {void}
 */
export function showLoading(message = "Chargement...") {
    console.log("Affichage du chargement:", message);
    
    // Créer ou mettre à jour l'élément de chargement
    let loadingElement = document.getElementById('global-loading-indicator');
    
    if (!loadingElement) {
        loadingElement = document.createElement('div');
        loadingElement.id = 'global-loading-indicator';
        loadingElement.style.position = 'fixed';
        loadingElement.style.top = '50%';
        loadingElement.style.left = '50%';
        loadingElement.style.transform = 'translate(-50%, -50%)';
        loadingElement.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        loadingElement.style.color = 'white';
        loadingElement.style.padding = '20px';
        loadingElement.style.borderRadius = '8px';
        loadingElement.style.zIndex = '9999';
        loadingElement.style.display = 'flex';
        loadingElement.style.alignItems = 'center';
        loadingElement.style.justifyContent = 'center';
        loadingElement.style.flexDirection = 'column';
        
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border text-light';
        spinner.style.width = '3rem';
        spinner.style.height = '3rem';
        spinner.style.marginBottom = '10px';
        spinner.role = 'status';
        
        const messageElement = document.createElement('span');
        messageElement.textContent = message;
        
        loadingElement.appendChild(spinner);
        loadingElement.appendChild(messageElement);
        document.body.appendChild(loadingElement);
    } else {
        const messageElement = loadingElement.querySelector('span');
        if (messageElement) {
            messageElement.textContent = message;
        }
        loadingElement.style.display = 'flex';
    }
}

/**
 * Masque l'indicateur de chargement.
 */
export function hideLoading() {
    const loadingElement = document.getElementById('global-loading-indicator');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

/**
 * Affiche un message toast.
 * @param {string} message - Message à afficher
 * @param {string} type - Type de toast ('success', 'error', 'info', 'warning')
 */
export function showToast(message, type = 'info') {
    console.log(`Toast ${type}:`, message);
    
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast show toast-${type}`;
    toast.style.minWidth = '250px';
    toast.style.marginBottom = '10px';
    
    const toastHeader = document.createElement('div');
    toastHeader.className = 'toast-header';
    toastHeader.style.backgroundColor = getToastHeaderColor(type);
    toastHeader.style.color = 'white';
    
    const toastTitle = document.createElement('strong');
    toastTitle.className = 'me-auto';
    toastTitle.textContent = getToastTitle(type);
    
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close btn-close-white';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');
    closeButton.addEventListener('click', () => {
        toast.remove();
    });
    
    toastHeader.appendChild(toastTitle);
    toastHeader.appendChild(closeButton);
    
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body';
    toastBody.textContent = message;
    
    toast.appendChild(toastHeader);
    toast.appendChild(toastBody);
    
    toastContainer.appendChild(toast);
    
    // Masquer automatiquement après 5 secondes
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

/**
 * Crée le conteneur pour les notifications toast
 * @returns {Object} Élément conteneur créé
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

/**
 * Récupère la couleur du header du toast selon le type
 * @param {string} type - Type de toast ('success', 'error', 'info', 'warning')
 * @returns {string} Code couleur hexadécimal
 */
function getToastHeaderColor(type) {
    const colors = {
        'success': '#28a745',
        'error': '#dc3545',
        'info': '#17a2b8',
        'warning': '#ffc107'
    };
    return colors[type] || colors['info'];
}

/**
 * Récupère le titre du toast selon le type
 * @param {string} type - Type de toast ('success', 'error', 'info', 'warning')
 * @returns {string} Titre à afficher
 */
function getToastTitle(type) {
    const titles = {
        'success': 'Succès',
        'error': 'Erreur',
        'info': 'Information',
        'warning': 'Attention'
    };
    return titles[type] || titles['info'];
}

/**
 * Basculer l'état actif d'un bouton.
 * @param {Object} button - Bouton à modifier
 * @param {boolean} isActive - État actuel du bouton
 * @returns {void}
 */
export function toggleActiveButton(button, isActive) {
    if (isActive) {
        button.classList.remove('active');
    } else {
        button.classList.add('active');
    }
}

/**
 * Sauvegarder l'état dans l'URL.
 * @param {object} state - État à sauvegarder
 */
export function saveStateToUrl(state) {
    const url = new URL(window.location.href);
    
    // Sauvegarder les propriétés de l'état
    for (const [key, value] of Object.entries(state)) {
        if (value !== null && value !== undefined && value !== '') {
            url.searchParams.set(key, String(value));
        } else {
            url.searchParams.delete(key);
        }
    }
    
    window.history.replaceState({}, '', url);
}

/**
 * Restaurer l'état depuis l'URL.
 * @returns {object} État restauré
 */
export function restoreStateFromUrl() {
    const url = new URL(window.location.href);
    const state = {};
    
    // Restaurer les paramètres
    url.searchParams.forEach((value, key) => {
        // Essayer de convertir en nombre ou booléen si possible
        if (value === 'true') {
            state[key] = true;
        } else if (value === 'false') {
            state[key] = false;
        } else if (!isNaN(value)) {
            state[key] = Number(value);
        } else {
            state[key] = value;
        }
    });
    
    return state;
}

/**
 * Mettre à jour les états actifs des boutons.
 * @param {object} activeFilters - Filtres actifs
 */
export function updateActiveButtonStates(activeFilters) {
    // Gérer les boutons de pâte
    document.querySelectorAll('[id^="filter-type_pate_"]').forEach(button => {
        const pateType = button.textContent.trim();
        if (activeFilters.type_pate === pateType) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // Gérer les boutons de saveur
    document.querySelectorAll('[id^="filter-type_saveur_"]').forEach(button => {
        const saveurType = button.textContent.trim();
        if (activeFilters.type_saveur === saveurType) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // Gérer les boutons de statut
    document.querySelectorAll('[id^="filter-"]:not([id^="filter-type_pate_"]):not([id^="filter-type_saveur_"]):not([id="filter-all"]):not([id="filter-pate-btn"]):not([id="filter-saveur-btn"]):not([id="filter-statut-btn"]):not([id="geolocate-me"])').forEach(button => {
        const buttonId = button.id;
        if (buttonId === 'filter-visited' && activeFilters.visited) {
            button.classList.add('active');
        } else if (buttonId === 'filter-unvisited' && activeFilters.unvisited) {
            button.classList.add('active');
        } else if (buttonId === 'filter-label' && activeFilters.label) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

/**
 * Mettre à jour la couleur des boutons principaux de filtre.
 * @param {object} activeFilters - Filtres actifs
 */
export function updateMainFilterButtons(activeFilters) {
    // Réinitialiser tous les boutons principaux
    document.getElementById('filter-pate-btn')?.classList.remove('active');
    document.getElementById('filter-saveur-btn')?.classList.remove('active');
    document.getElementById('filter-statut-btn')?.classList.remove('active');

    // Mettre en bleu les boutons dont la catégorie a des filtres actifs
    if (activeFilters.type_pate) {
        document.getElementById('filter-pate-btn')?.classList.add('active');
    }
    if (activeFilters.type_saveur) {
        document.getElementById('filter-saveur-btn')?.classList.add('active');
    }
    if (activeFilters.visited || activeFilters.unvisited || activeFilters.label) {
        document.getElementById('filter-statut-btn')?.classList.add('active');
    }
}

/**
 * Fonction pour gérer la navigation avec fallback.
 * @param {string} fallbackUrl - URL de fallback
 */
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

// Ajouter la fonction au scope global pour compatibilité avec les scripts inline
window.goBackOrRedirect = goBackOrRedirect;

// Export pour les modules ES6
export { goBackOrRedirect };

// Export pour compatibilité avec les anciens scripts
document.utils = {
    debounce,
    showLoading,
    hideLoading,
    showToast,
    toggleActiveButton,
    saveStateToUrl,
    restoreStateFromUrl,
    updateActiveButtonStates,
    updateMainFilterButtons,
    goBackOrRedirect
};
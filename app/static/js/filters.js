/**
 * Module de gestion des filtres pour l'application PlanFlan
 * 
 * Ce module gère les filtres de la carte et leur interaction avec les marqueurs
 */

import { updateActiveButtonStates, updateMainFilterButtons, toggleActiveButton } from './utils.js';
import { updateMarkersBasedOnFilters as updateMapMarkers, saveCompleteStateToUrl, setActiveFilters as setMapActiveFilters } from './map.js';

// État des filtres actifs
let activeFilters = {
    type_pate: false,
    type_saveur: false,
    visited: false,
    unvisited: false,
    label: false
};

/**
 * Met à jour les marqueurs en fonction des filtres actifs.
 * Affiche ou masque les marqueurs selon les critères de filtrage sélectionnés.
 */
function updateMarkersBasedOnFilters() {
    // Synchroniser les filtres avec map.js
    setMapActiveFilters(activeFilters);
    // Appeler la fonction de map.js pour mettre à jour les marqueurs
    updateMapMarkers();
    updateActiveButtonStates(activeFilters);
    updateMainFilterButtons(activeFilters);
}

/**
 * Fonction pour configurer les boutons de pâte
 */
export function setupPateButtons() {
    const pateButtons = {
        'Feuilletée': 'filter-type_pate_FEUILLETEE',
        'Brisée': 'filter-type_pate_BRISEE',
        'Sucrée': 'filter-type_pate_SUCREE',
        'Sablée': 'filter-type_pate_SABLEE',
        'Mixte': 'filter-type_pate_MIXTE'
    };

    Object.entries(pateButtons).forEach(([pateType, buttonId]) => {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', function() {
                const isActive = activeFilters.type_pate === pateType;
                activeFilters.type_pate = isActive ? false : pateType;
                // Ne plus désactiver les autres filtres - permettre la combinaison
                updateMarkersBasedOnFilters();
                toggleActiveButton(this, isActive);
                
                // Sauvegarder l'état dans l'URL
                saveCompleteStateToUrl();
            });
        }
    });
}

/**
 * Fonction pour configurer les boutons de saveur
 */
export function setupSaveurButtons() {
    const saveurButtons = {
        'Vanille': 'filter-type_saveur_VANILLE',
        'Chocolat': 'filter-type_saveur_CHOCOLAT',
        'Noix': 'filter-type_saveur_NOIX',
        'Fruits': 'filter-type_saveur_FRUITS',
        'Insolite': 'filter-type_saveur_INSOLITE',
        'Nature': 'filter-type_saveur_NATURE'
    };

    Object.entries(saveurButtons).forEach(([saveurType, buttonId]) => {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', function() {
                const isActive = activeFilters.type_saveur === saveurType;
                activeFilters.type_saveur = isActive ? false : saveurType;
                // Ne plus désactiver les autres filtres - permettre la combinaison
                updateMarkersBasedOnFilters();
                toggleActiveButton(this, isActive);
                
                // Sauvegarder l'état dans l'URL
                saveCompleteStateToUrl();
            });
        }
    });
}

/**
 * Fonction pour configurer les boutons de statut
 */
export function setupStatutButtons() {
    const statutButtons = {
        'visited': 'filter-visited',
        'unvisited': 'filter-unvisited',
        'label': 'filter-label'
    };

    Object.entries(statutButtons).forEach(([statutType, buttonId]) => {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', function() {
                const isActive = activeFilters[statutType];
                activeFilters[statutType] = !isActive;

                // Désactiver les autres filtres de statut si nécessaire
                if (!isActive) {
                    Object.keys(statutButtons).filter(key => key !== statutType)
                        .forEach(key => activeFilters[key] = false);
                }
                // Ne plus désactiver les filtres de pâte/saveur - permettre la combinaison

                updateMarkersBasedOnFilters();
                toggleActiveButton(this, isActive);
                
                // Sauvegarder l'état dans l'URL
                saveCompleteStateToUrl();
            });
        }
    });
}

/**
 * Fonction pour configurer les boutons de filtre
 */
export function setupFilterButtons() {
    // Ajouter la classe filter-btn à tous les boutons de filtre
    const filterButtons = document.querySelectorAll('#filter-controls button');
    filterButtons.forEach(button => {
        button.classList.add('filter-btn');
    });

    const filterAllButton = document.getElementById('filter-all');
    if (filterAllButton) {
        filterAllButton.addEventListener('click', function() {
            activeFilters = { type_pate: false, type_saveur: false, visited: false, unvisited: false, label: false};
            updateMarkersBasedOnFilters();
            const subFilters = document.getElementById('sub-filters');
            if (subFilters) {
                subFilters.classList.remove('show');
            }
            updateActiveButtonStates(activeFilters);
            updateMainFilterButtons(activeFilters);
            
            // Sauvegarder l'état dans l'URL
            saveCompleteStateToUrl();
        });
    }

    // Bouton pour afficher/masquer les options de pâte
    const filterPateBtn = document.getElementById('filter-pate-btn');
    if (filterPateBtn) {
        filterPateBtn.addEventListener('click', function() {
            const subFilters = document.getElementById('sub-filters');
            if (subFilters) {
                if (subFilters.classList.contains('show') && subFilters.querySelector('.filter-group')) {
                    subFilters.classList.remove('show');
                } else {
                    subFilters.innerHTML = `
                        <div class="filter-group">
                            <button id="filter-type_pate_FEUILLETEE" class="btn btn-success">Feuilletée</button>
                            <button id="filter-type_pate_BRISEE" class="btn btn-success">Brisée</button>
                            <button id="filter-type_pate_SUCREE" class="btn btn-success">Sucrée</button>
                            <button id="filter-type_pate_SABLEE" class="btn btn-success">Sablée</button>
                            <button id="filter-type_pate_MIXTE" class="btn btn-success">Mixte</button>
                        </div>
                    `;
                    subFilters.classList.add('show');
                    setupPateButtons();
                    updateActiveButtonStates(activeFilters); // ← Restaurer les états actifs
                    updateMainFilterButtons(activeFilters); // ← Mettre à jour les boutons principaux
                }
            }
        });
    }

    // Bouton pour afficher/masquer les options de saveur
    const filterSaveurBtn = document.getElementById('filter-saveur-btn');
    if (filterSaveurBtn) {
        filterSaveurBtn.addEventListener('click', function() {
            const subFilters = document.getElementById('sub-filters');
            if (subFilters) {
                if (subFilters.classList.contains('show') && subFilters.querySelector('.filter-group')) {
                    subFilters.classList.remove('show');
                } else {
                    subFilters.innerHTML = `
                        <div class="filter-group">
                            <button id="filter-type_saveur_VANILLE" class="btn btn-success">Vanille</button>
                            <button id="filter-type_saveur_CHOCOLAT" class="btn btn-success">Chocolat</button>
                            <button id="filter-type_saveur_NOIX" class="btn btn-success">Noix</button>
                            <button id="filter-type_saveur_FRUITS" class="btn btn-success">Fruits</button>
                            <button id="filter-type_saveur_INSOLITE" class="btn btn-success">Insolite</button>
                            <button id="filter-type_saveur_NATURE" class="btn btn-success">Nature</button>
                        </div>
                    `;
                    subFilters.classList.add('show');
                    setupSaveurButtons();
                    updateActiveButtonStates(activeFilters); // ← Restaurer les états actifs
                    updateMainFilterButtons(activeFilters); // ← Mettre à jour les boutons principaux
                }
            }
        });
    }

    // Bouton pour afficher/masquer les options de statut
    const filterStatutBtn = document.getElementById('filter-statut-btn');
    if (filterStatutBtn) {
        filterStatutBtn.addEventListener('click', function() {
            const subFilters = document.getElementById('sub-filters');
            if (subFilters) {
                if (subFilters.classList.contains('show') && subFilters.querySelector('.filter-group')) {
                    subFilters.classList.remove('show');
                } else {
                    subFilters.innerHTML = `
                        <div class="filter-group">
                            <button id="filter-visited" class="btn btn-success">Visité</button>
                            <button id="filter-unvisited" class="btn btn-success">Non visité</button>
                            <button id="filter-label" class="btn btn-success">Labellisé</button>
                        </div>
                    `;
                    subFilters.classList.add('show');
                    setupStatutButtons();
                    updateActiveButtonStates(activeFilters); // ← Restaurer les états actifs
                    updateMainFilterButtons(activeFilters); // ← Mettre à jour les boutons principaux
                }
            }
        });
    }

    document.addEventListener('click', function(event) {
        const subFilters = document.getElementById('sub-filters');
        const filterPateBtn = document.getElementById('filter-pate-btn');
        const filterSaveurBtn = document.getElementById('filter-saveur-btn');
        const filterStatutBtn = document.getElementById('filter-statut-btn');

        // Si le clic n'est pas sur un bouton de filtre ou dans les sous-filtres, on masque les sous-filtres
        if (subFilters && !filterPateBtn?.contains(event.target) &&
            !filterSaveurBtn?.contains(event.target) &&
            !filterStatutBtn?.contains(event.target) &&
            !subFilters.contains(event.target)) {
            subFilters.classList.remove('show');
        }
    });
}

/**
 * Fonction pour restaurer l'état des filtres depuis l'URL
 */
export function restoreFiltersFromUrl() {
    const url = new URL(window.location.href);
    
    // Restaurer les filtres
    if (url.searchParams.has('pate')) {
        activeFilters.type_pate = url.searchParams.get('pate');
    }
    
    if (url.searchParams.has('saveur')) {
        activeFilters.type_saveur = url.searchParams.get('saveur');
    }
    
    if (url.searchParams.has('visited')) {
        activeFilters.visited = url.searchParams.get('visited') === 'true';
    }
    
    if (url.searchParams.has('unvisited')) {
        activeFilters.unvisited = url.searchParams.get('unvisited') === 'true';
    }
    
    if (url.searchParams.has('label')) {
        activeFilters.label = url.searchParams.get('label') === 'true';
    }
    
    return activeFilters;
}

/**
 * Fonction pour obtenir les filtres actifs
 * @returns {object} Filtres actifs
 */
export function getActiveFilters() {
    return activeFilters;
}

/**
 * Fonction pour définir les filtres actifs
 * @param {object} newFilters - Nouveaux filtres à appliquer
 */
export function setActiveFilters(newFilters) {
    activeFilters = { ...activeFilters, ...newFilters };
}

// Export pour compatibilité avec les anciens scripts
document.filters = {
    setupFilterButtons,
    setupPateButtons,
    setupSaveurButtons,
    setupStatutButtons,
    restoreFiltersFromUrl,
    getActiveFilters,
    setActiveFilters
};
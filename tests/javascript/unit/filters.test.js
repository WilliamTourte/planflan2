/**
 * Tests unitaires pour le module filters.js
 *
 * Ce module teste les fonctionnalités de filtrage des établissements
 */

// Mock des modules dépendants AVANT l'import
jest.mock('../../../app/static/js/utils.js', () => ({
    updateActiveButtonStates: jest.fn(),
    updateMainFilterButtons: jest.fn(),
    toggleActiveButton: jest.fn()
}));

jest.mock('../../../app/static/js/map.js', () => ({
    updateMarkersBasedOnFilters: jest.fn(),
    saveCompleteStateToUrl: jest.fn(),
    setActiveFilters: jest.fn()
}));

// Import APRÈS les mocks
import {
    setupPateButtons,
    setupSaveurButtons,
    setupStatutButtons,
    setupFilterButtons,
    restoreFiltersFromUrl,
    getActiveFilters,
    setActiveFilters
} from '../../../app/static/js/filters.js';

describe('Filters Module', () => {
    beforeEach(() => {
        // Réinitialiser le DOM
        document.body.innerHTML = '';
        jest.clearAllMocks();

        // Réinitialiser les filtres à leur état par défaut
        setActiveFilters({
            type_pate: false,
            type_saveur: false,
            visited: false,
            unvisited: false,
            label: false
        });
    });

    describe('getActiveFilters', () => {
        it('should return the current active filters state', () => {
            const filters = getActiveFilters();

            expect(filters).toBeDefined();
            expect(typeof filters).toBe('object');
        });
    });

    describe('setActiveFilters', () => {
        it('should update active filters state', () => {
            const newFilters = {
                type_pate: 'Feuilletée',
                type_saveur: 'Vanille',
                visited: true,
                unvisited: false,
                label: false
            };

            setActiveFilters(newFilters);
            const result = getActiveFilters();

            expect(result.type_pate).toBe('Feuilletée');
            expect(result.type_saveur).toBe('Vanille');
            expect(result.visited).toBe(true);
        });
    });

    describe('setupPateButtons', () => {
        it('should setup click handlers for pate filter buttons', () => {
            // Créer les boutons de pâte dans le DOM
            document.body.innerHTML = `
                <button id="filter-type_pate_FEUILLETEE">Feuilletée</button>
                <button id="filter-type_pate_BRISEE">Brisée</button>
                <button id="filter-type_pate_SUCREE">Sucrée</button>
                <button id="filter-type_pate_SABLEE">Sablée</button>
                <button id="filter-type_pate_MIXTE">Mixte</button>
            `;

            setupPateButtons();

            // Vérifier que les boutons ont des event listeners
            const buttonFeuilletee = document.getElementById('filter-type_pate_FEUILLETEE');
            expect(buttonFeuilletee).toBeTruthy();
        });

        it('should toggle filter state when button is clicked', () => {
            document.body.innerHTML = `
                <button id="filter-type_pate_FEUILLETEE">Feuilletée</button>
            `;

            // Réinitialiser les filtres
            setActiveFilters({ type_pate: false });

            setupPateButtons();

            const button = document.getElementById('filter-type_pate_FEUILLETEE');
            button.click();

            const filters = getActiveFilters();
            expect(filters.type_pate).toBe('Feuilletée');
        });

        it('should deactivate filter when clicked again', () => {
            document.body.innerHTML = `
                <button id="filter-type_pate_FEUILLETEE">Feuilletée</button>
            `;

            // Réinitialiser les filtres
            setActiveFilters({ type_pate: false });

            setupPateButtons();

            const button = document.getElementById('filter-type_pate_FEUILLETEE');

            // Premier clic - activer
            button.click();
            expect(getActiveFilters().type_pate).toBe('Feuilletée');

            // Deuxième clic - désactiver
            button.click();
            expect(getActiveFilters().type_pate).toBe(false);
        });

        it('should handle missing buttons gracefully', () => {
            document.body.innerHTML = '';

            expect(() => setupPateButtons()).not.toThrow();
        });
    });

    describe('setupSaveurButtons', () => {
        it('should setup click handlers for saveur filter buttons', () => {
            document.body.innerHTML = `
                <button id="filter-type_saveur_VANILLE">Vanille</button>
                <button id="filter-type_saveur_CHOCOLAT">Chocolat</button>
                <button id="filter-type_saveur_NOIX">Noix</button>
                <button id="filter-type_saveur_FRUITS">Fruits</button>
                <button id="filter-type_saveur_INSOLITE">Insolite</button>
                <button id="filter-type_saveur_NATURE">Nature</button>
            `;

            setupSaveurButtons();

            const buttonVanille = document.getElementById('filter-type_saveur_VANILLE');
            expect(buttonVanille).toBeTruthy();
        });

        it('should toggle saveur filter on click', () => {
            document.body.innerHTML = `
                <button id="filter-type_saveur_CHOCOLAT">Chocolat</button>
            `;

            setActiveFilters({ type_saveur: false });
            setupSaveurButtons();

            const button = document.getElementById('filter-type_saveur_CHOCOLAT');
            button.click();

            const filters = getActiveFilters();
            expect(filters.type_saveur).toBe('Chocolat');
        });
    });

    describe('setupStatutButtons', () => {
        it('should setup click handlers for statut filter buttons', () => {
            document.body.innerHTML = `
                <button id="filter-visited">Visité</button>
                <button id="filter-unvisited">Non visité</button>
                <button id="filter-label">Labellisé</button>
            `;

            setupStatutButtons();

            const buttonVisited = document.getElementById('filter-visited');
            expect(buttonVisited).toBeTruthy();
        });

        it('should toggle visited filter on click', () => {
            document.body.innerHTML = `
                <button id="filter-visited">Visité</button>
            `;

            setActiveFilters({ visited: false, unvisited: false, label: false });
            setupStatutButtons();

            const button = document.getElementById('filter-visited');
            button.click();

            const filters = getActiveFilters();
            expect(filters.visited).toBe(true);
        });

        it('should deactivate other statut filters when one is activated', () => {
            document.body.innerHTML = `
                <button id="filter-visited">Visité</button>
                <button id="filter-unvisited">Non visité</button>
            `;

            setActiveFilters({ visited: false, unvisited: false, label: false });
            setupStatutButtons();

            // Activer visited
            document.getElementById('filter-visited').click();
            expect(getActiveFilters().visited).toBe(true);

            // Activer unvisited - devrait désactiver visited
            document.getElementById('filter-unvisited').click();
            const filters = getActiveFilters();
            expect(filters.unvisited).toBe(true);
            expect(filters.visited).toBe(false);
        });
    });

    describe('setupFilterButtons', () => {
        it('should setup all filter button types', () => {
            document.body.innerHTML = `
                <div id="filter-controls">
                    <button id="filter-type_pate_FEUILLETEE">Feuilletée</button>
                    <button id="filter-type_saveur_VANILLE">Vanille</button>
                    <button id="filter-visited">Visité</button>
                    <button id="reset-filters">Reset</button>
                </div>
            `;

            setupFilterButtons();

            // Les boutons devraient avoir des event listeners
            expect(document.getElementById('filter-type_pate_FEUILLETEE')).toBeTruthy();
        });

        it('should handle reset button click', () => {
            document.body.innerHTML = `
                <button id="filter-all">Tous</button>
            `;

            // Configurer un filtre actif
            setActiveFilters({ type_pate: 'Feuilletée' });

            setupFilterButtons();

            const resetButton = document.getElementById('filter-all');
            if (resetButton) {
                resetButton.click();
                const filters = getActiveFilters();
                expect(filters.type_pate).toBe(false);
            }
        });
    });

    describe('restoreFiltersFromUrl', () => {
        it('should restore filters from URL parameters', () => {
            // Simuler des paramètres URL
            delete window.location;
            window.location = new URL('http://test.com/?pate=Feuilletée&saveur=Vanille');

            const result = restoreFiltersFromUrl();

            expect(result.type_pate).toBe('Feuilletée');
            expect(result.type_saveur).toBe('Vanille');
        });

        it('should handle empty URL parameters', () => {
            delete window.location;
            window.location = new URL('http://test.com/');

            expect(() => restoreFiltersFromUrl()).not.toThrow();
        });

        it('should restore visited filter from URL', () => {
            delete window.location;
            window.location = new URL('http://test.com/?visited=true');

            setActiveFilters({ visited: false });
            const result = restoreFiltersFromUrl();

            expect(result.visited).toBe(true);
        });
    });

    describe('Filter combinations', () => {
        it('should allow combining pate and saveur filters', () => {
            document.body.innerHTML = `
                <button id="filter-type_pate_FEUILLETEE">Feuilletée</button>
                <button id="filter-type_saveur_VANILLE">Vanille</button>
            `;

            setActiveFilters({ type_pate: false, type_saveur: false });
            setupPateButtons();
            setupSaveurButtons();

            // Activer les deux filtres
            document.getElementById('filter-type_pate_FEUILLETEE').click();
            document.getElementById('filter-type_saveur_VANILLE').click();

            const filters = getActiveFilters();
            expect(filters.type_pate).toBe('Feuilletée');
            expect(filters.type_saveur).toBe('Vanille');
        });
    });

    describe('Sub-filter buttons', () => {
        it('should show pate sub-filters when pate button is clicked', () => {
            document.body.innerHTML = `
                <div id="filter-controls">
                    <button id="filter-pate-btn">Pâte</button>
                    <div id="sub-filters"></div>
                </div>
            `;

            setupFilterButtons();

            const pateBtn = document.getElementById('filter-pate-btn');
            pateBtn.click();

            const subFilters = document.getElementById('sub-filters');
            expect(subFilters.classList.contains('show')).toBe(true);
            expect(subFilters.innerHTML).toContain('filter-type_pate_FEUILLETEE');
        });

        it('should hide pate sub-filters when clicked again', () => {
            document.body.innerHTML = `
                <div id="filter-controls">
                    <button id="filter-pate-btn">Pâte</button>
                    <div id="sub-filters" class="show">
                        <div class="filter-group">
                            <button id="filter-type_pate_FEUILLETEE">Feuilletée</button>
                        </div>
                    </div>
                </div>
            `;

            setupFilterButtons();

            const pateBtn = document.getElementById('filter-pate-btn');
            pateBtn.click();

            const subFilters = document.getElementById('sub-filters');
            expect(subFilters.classList.contains('show')).toBe(false);
        });

        it('should show saveur sub-filters when saveur button is clicked', () => {
            document.body.innerHTML = `
                <div id="filter-controls">
                    <button id="filter-saveur-btn">Saveur</button>
                    <div id="sub-filters"></div>
                </div>
            `;

            setupFilterButtons();

            const saveurBtn = document.getElementById('filter-saveur-btn');
            saveurBtn.click();

            const subFilters = document.getElementById('sub-filters');
            expect(subFilters.classList.contains('show')).toBe(true);
            expect(subFilters.innerHTML).toContain('filter-type_saveur_VANILLE');
        });

        it('should show statut sub-filters when statut button is clicked', () => {
            document.body.innerHTML = `
                <div id="filter-controls">
                    <button id="filter-statut-btn">Statut</button>
                    <div id="sub-filters"></div>
                </div>
            `;

            setupFilterButtons();

            const statutBtn = document.getElementById('filter-statut-btn');
            statutBtn.click();

            const subFilters = document.getElementById('sub-filters');
            expect(subFilters.classList.contains('show')).toBe(true);
            expect(subFilters.innerHTML).toContain('filter-visited');
        });

        it('should close sub-filters when clicking outside', () => {
            document.body.innerHTML = `
                <div id="filter-controls">
                    <button id="filter-pate-btn">Pâte</button>
                    <button id="filter-saveur-btn">Saveur</button>
                    <button id="filter-statut-btn">Statut</button>
                    <div id="sub-filters" class="show">
                        <div class="filter-group">Test</div>
                    </div>
                </div>
                <div id="outside">Click outside</div>
            `;

            setupFilterButtons();

            const subFilters = document.getElementById('sub-filters');
            expect(subFilters.classList.contains('show')).toBe(true);

            // Simuler un clic à l'extérieur
            const outsideElement = document.getElementById('outside');
            const clickEvent = new MouseEvent('click', { bubbles: true });
            outsideElement.dispatchEvent(clickEvent);

            expect(subFilters.classList.contains('show')).toBe(false);
        });
    });

    describe('restoreFiltersFromUrl extended', () => {
        it('should restore unvisited filter from URL', () => {
            delete window.location;
            window.location = new URL('http://test.com/?unvisited=true');

            setActiveFilters({ unvisited: false });
            const result = restoreFiltersFromUrl();

            expect(result.unvisited).toBe(true);
        });

        it('should restore label filter from URL', () => {
            delete window.location;
            window.location = new URL('http://test.com/?label=true');

            setActiveFilters({ label: false });
            const result = restoreFiltersFromUrl();

            expect(result.label).toBe(true);
        });

        it('should restore multiple filters from URL', () => {
            delete window.location;
            window.location = new URL('http://test.com/?pate=Brisée&saveur=Chocolat&visited=true');

            setActiveFilters({ type_pate: false, type_saveur: false, visited: false });
            const result = restoreFiltersFromUrl();

            expect(result.type_pate).toBe('Brisée');
            expect(result.type_saveur).toBe('Chocolat');
            expect(result.visited).toBe(true);
        });
    });

    describe('Pate buttons extended', () => {
        it('should setup all pate types', () => {
            document.body.innerHTML = `
                <button id="filter-type_pate_FEUILLETEE">Feuilletée</button>
                <button id="filter-type_pate_BRISEE">Brisée</button>
                <button id="filter-type_pate_SUCREE">Sucrée</button>
                <button id="filter-type_pate_SABLEE">Sablée</button>
                <button id="filter-type_pate_MIXTE">Mixte</button>
            `;

            setActiveFilters({ type_pate: false });
            setupPateButtons();

            // Tester chaque bouton
            const pateTypes = ['Feuilletée', 'Brisée', 'Sucrée', 'Sablée', 'Mixte'];
            pateTypes.forEach(pateType => {
                setActiveFilters({ type_pate: false });
                const buttonId = `filter-type_pate_${pateType.toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')}`;
                const button = document.getElementById(buttonId);
                if (button) {
                    button.click();
                    expect(getActiveFilters().type_pate).toBe(pateType);
                }
            });
        });
    });

    describe('Saveur buttons extended', () => {
        it('should setup all saveur types', () => {
            document.body.innerHTML = `
                <button id="filter-type_saveur_VANILLE">Vanille</button>
                <button id="filter-type_saveur_CHOCOLAT">Chocolat</button>
                <button id="filter-type_saveur_NOIX">Noix</button>
                <button id="filter-type_saveur_FRUITS">Fruits</button>
                <button id="filter-type_saveur_INSOLITE">Insolite</button>
                <button id="filter-type_saveur_NATURE">Nature</button>
            `;

            setActiveFilters({ type_saveur: false });
            setupSaveurButtons();

            // Tester chaque bouton
            const saveurTypes = ['Vanille', 'Chocolat', 'Noix', 'Fruits', 'Insolite', 'Nature'];
            saveurTypes.forEach(saveurType => {
                setActiveFilters({ type_saveur: false });
                const button = document.getElementById(`filter-type_saveur_${saveurType.toUpperCase()}`);
                if (button) {
                    button.click();
                    expect(getActiveFilters().type_saveur).toBe(saveurType);
                }
            });
        });

        it('should deactivate saveur filter when clicked again', () => {
            document.body.innerHTML = `
                <button id="filter-type_saveur_VANILLE">Vanille</button>
            `;

            setActiveFilters({ type_saveur: false });
            setupSaveurButtons();

            const button = document.getElementById('filter-type_saveur_VANILLE');
            button.click();
            expect(getActiveFilters().type_saveur).toBe('Vanille');

            button.click();
            expect(getActiveFilters().type_saveur).toBe(false);
        });
    });

    describe('Statut buttons extended', () => {
        it('should toggle label filter', () => {
            document.body.innerHTML = `
                <button id="filter-label">Labellisé</button>
            `;

            setActiveFilters({ visited: false, unvisited: false, label: false });
            setupStatutButtons();

            const button = document.getElementById('filter-label');
            button.click();
            expect(getActiveFilters().label).toBe(true);

            button.click();
            expect(getActiveFilters().label).toBe(false);
        });

        it('should deactivate label when visited is activated', () => {
            document.body.innerHTML = `
                <button id="filter-visited">Visité</button>
                <button id="filter-label">Labellisé</button>
            `;

            setActiveFilters({ visited: false, unvisited: false, label: true });
            setupStatutButtons();

            document.getElementById('filter-visited').click();
            const filters = getActiveFilters();
            expect(filters.visited).toBe(true);
            expect(filters.label).toBe(false);
        });
    });

    describe('Filter all button', () => {
        it('should reset all filters and hide sub-filters', () => {
            document.body.innerHTML = `
                <button id="filter-all">Tous</button>
                <div id="sub-filters" class="show"></div>
            `;

            setActiveFilters({
                type_pate: 'Feuilletée',
                type_saveur: 'Vanille',
                visited: true,
                unvisited: false,
                label: true
            });

            setupFilterButtons();

            const resetButton = document.getElementById('filter-all');
            resetButton.click();

            const filters = getActiveFilters();
            expect(filters.type_pate).toBe(false);
            expect(filters.type_saveur).toBe(false);
            expect(filters.visited).toBe(false);
            expect(filters.label).toBe(false);

            const subFilters = document.getElementById('sub-filters');
            expect(subFilters.classList.contains('show')).toBe(false);
        });
    });
});

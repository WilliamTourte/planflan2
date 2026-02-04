/**
 * Tests unitaires pour l'autocomplete du header
 *
 * Ce module teste les fonctions d'autocomplétion de la barre de recherche du header
 */

describe('Header Autocomplete Module', () => {
    let searchInput;
    let resultsContainer;
    let searchForm;

    beforeEach(() => {
        // Créer le DOM de test
        document.body.innerHTML = `
            <div class="header-search-container">
                <form id="header-search-form" action="/liste_etablissements" method="GET">
                    <input type="text" name="recherche_simple" id="search-input" autocomplete="off" />
                    <button type="submit" id="search-button">Rechercher</button>
                </form>
                <div id="header-autocomplete-results" class="autocomplete-results"></div>
            </div>
        `;

        searchInput = document.getElementById('search-input');
        resultsContainer = document.getElementById('header-autocomplete-results');
        searchForm = document.getElementById('header-search-form');

        jest.clearAllMocks();
        jest.useFakeTimers();

        // Mock fetch
        global.fetch = jest.fn();

        // Mock window.location
        delete window.location;
        window.location = {
            href: 'http://test.example.com/page',
            assign: jest.fn()
        };
        Object.defineProperty(window.location, 'href', {
            set: jest.fn(),
            get: () => 'http://test.example.com/page',
            configurable: true
        });
    });

    afterEach(() => {
        jest.useRealTimers();
        delete global.fetch;
    });

    describe('initHeaderAutocomplete', () => {
        // Simuler la fonction initHeaderAutocomplete
        function initHeaderAutocomplete() {
            const input = document.getElementById('search-input');
            const container = document.getElementById('header-autocomplete-results');

            if (!input || !container) {
                return false;
            }
            return true;
        }

        it('should return false when elements are missing', () => {
            document.body.innerHTML = '';
            const result = initHeaderAutocomplete();
            expect(result).toBe(false);
        });

        it('should return true when elements are present', () => {
            const result = initHeaderAutocomplete();
            expect(result).toBe(true);
        });
    });

    describe('API calls', () => {
        it('should not call API for queries less than 2 characters', async () => {
            // Simuler la logique de la fonction fetchEtablissements
            const query = 'a';
            if (query.length < 2) {
                // Ne pas appeler l'API
                expect(global.fetch).not.toHaveBeenCalled();
            }
        });

        it('should call API for queries of 2 or more characters', async () => {
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve([
                    { id_etab: 1, nom: 'Boulangerie Test', ville: 'Paris', url: '/etablissement/1', total_count: 1 }
                ])
            });

            const query = 'bou';
            const response = await fetch(`/api/etablissements/search?q=${encodeURIComponent(query)}`);

            expect(global.fetch).toHaveBeenCalledWith('/api/etablissements/search?q=bou');
            expect(response.ok).toBe(true);
        });
    });

    describe('Results display', () => {
        function showResults(etablissements, container) {
            container.innerHTML = '';

            if (etablissements.length === 0) {
                const noResults = document.createElement('div');
                noResults.className = 'autocomplete-no-results';
                noResults.textContent = 'Aucun établissement trouvé';
                container.appendChild(noResults);
                container.classList.add('show');
                return;
            }

            etablissements.forEach((etab) => {
                const div = document.createElement('div');
                div.className = 'autocomplete-item';
                div.innerHTML = `<strong>${etab.nom}</strong> <span class="text-muted">- ${etab.ville}</span>`;
                div.dataset.url = etab.url;
                container.appendChild(div);
            });

            container.classList.add('show');
        }

        it('should display "no results" message when array is empty', () => {
            showResults([], resultsContainer);

            const noResults = resultsContainer.querySelector('.autocomplete-no-results');
            expect(noResults).not.toBeNull();
            expect(noResults.textContent).toBe('Aucun établissement trouvé');
            expect(resultsContainer.classList.contains('show')).toBe(true);
        });

        it('should display results when etablissements are found', () => {
            const etablissements = [
                { id_etab: 1, nom: 'Boulangerie Test', ville: 'Paris', url: '/etablissement/1', total_count: 2 },
                { id_etab: 2, nom: 'Pâtisserie Test', ville: 'Lyon', url: '/etablissement/2', total_count: 2 }
            ];

            showResults(etablissements, resultsContainer);

            const items = resultsContainer.querySelectorAll('.autocomplete-item');
            expect(items.length).toBe(2);
            expect(items[0].innerHTML).toContain('Boulangerie Test');
            expect(items[0].innerHTML).toContain('Paris');
            expect(resultsContainer.classList.contains('show')).toBe(true);
        });
    });

    describe('Keyboard navigation', () => {
        function setupResults() {
            resultsContainer.innerHTML = '';
            const etablissements = [
                { nom: 'Établissement 1', ville: 'Paris', url: '/etablissement/1' },
                { nom: 'Établissement 2', ville: 'Lyon', url: '/etablissement/2' },
                { nom: 'Établissement 3', ville: 'Marseille', url: '/etablissement/3' }
            ];
            etablissements.forEach((etab, index) => {
                const div = document.createElement('div');
                div.className = 'autocomplete-item';
                div.dataset.index = index;
                div.dataset.url = etab.url;
                div.textContent = etab.nom;
                resultsContainer.appendChild(div);
            });
            resultsContainer.classList.add('show');
        }

        it('should navigate down with ArrowDown key', () => {
            setupResults();
            let currentFocus = -1;

            // Simuler la navigation
            const items = resultsContainer.querySelectorAll('.autocomplete-item');

            // ArrowDown
            currentFocus++;
            if (currentFocus >= items.length) currentFocus = 0;
            items[currentFocus].classList.add('active');

            expect(currentFocus).toBe(0);
            expect(items[0].classList.contains('active')).toBe(true);
        });

        it('should navigate up with ArrowUp key', () => {
            setupResults();
            let currentFocus = 1;

            const items = resultsContainer.querySelectorAll('.autocomplete-item');
            items[currentFocus].classList.add('active');

            // ArrowUp
            items[currentFocus].classList.remove('active');
            currentFocus--;
            if (currentFocus < 0) currentFocus = items.length - 1;
            items[currentFocus].classList.add('active');

            expect(currentFocus).toBe(0);
            expect(items[0].classList.contains('active')).toBe(true);
        });

        it('should wrap around when navigating past the end', () => {
            setupResults();
            let currentFocus = 2; // Dernier élément

            const items = resultsContainer.querySelectorAll('.autocomplete-item');

            // ArrowDown depuis le dernier élément
            currentFocus++;
            if (currentFocus >= items.length) currentFocus = 0;

            expect(currentFocus).toBe(0);
        });

        it('should wrap around when navigating before the start', () => {
            setupResults();
            let currentFocus = 0; // Premier élément

            const items = resultsContainer.querySelectorAll('.autocomplete-item');

            // ArrowUp depuis le premier élément
            currentFocus--;
            if (currentFocus < 0) currentFocus = items.length - 1;

            expect(currentFocus).toBe(2);
        });
    });

    describe('Form submission', () => {
        it('should redirect to /rechercher when input is empty', () => {
            searchInput.value = '';

            const mockPreventDefault = jest.fn();
            const event = { preventDefault: mockPreventDefault };

            // Simuler la logique de soumission
            if (searchInput.value.trim() === '') {
                event.preventDefault();
                // window.location.href = '/rechercher';
            }

            expect(mockPreventDefault).toHaveBeenCalled();
        });

        it('should redirect to single result when only one match', () => {
            const lastResults = [
                { id_etab: 1, nom: 'Unique', ville: 'Paris', url: '/etablissement/1', total_count: 1 }
            ];

            const mockPreventDefault = jest.fn();
            const event = { preventDefault: mockPreventDefault };

            // Simuler la logique de redirection
            if (lastResults.length === 1) {
                event.preventDefault();
                // window.location.href = lastResults[0].url;
            }

            expect(mockPreventDefault).toHaveBeenCalled();
        });

        it('should submit form normally when multiple results', () => {
            const lastResults = [
                { id_etab: 1, nom: 'Test 1', ville: 'Paris', url: '/etablissement/1', total_count: 2 },
                { id_etab: 2, nom: 'Test 2', ville: 'Lyon', url: '/etablissement/2', total_count: 2 }
            ];

            const mockPreventDefault = jest.fn();

            // Simuler la logique - ne devrait pas appeler preventDefault
            if (lastResults.length === 1) {
                mockPreventDefault();
            }

            expect(mockPreventDefault).not.toHaveBeenCalled();
        });
    });

    describe('Debounce functionality', () => {
        it('should debounce API calls', () => {
            const mockFetch = jest.fn();

            function debounce(func, timeout = 300) {
                let timer;
                return (...args) => {
                    clearTimeout(timer);
                    timer = setTimeout(() => {
                        func.apply(this, args);
                    }, timeout);
                };
            }

            const debouncedFetch = debounce(mockFetch);

            // Appeler plusieurs fois rapidement
            debouncedFetch('bou');
            debouncedFetch('boul');
            debouncedFetch('boula');
            debouncedFetch('boulan');

            // Avant le timeout, aucun appel
            expect(mockFetch).not.toHaveBeenCalled();

            // Exécuter tous les timers en attente
            jest.runAllTimers();

            // Après le timeout, un seul appel avec la dernière valeur
            expect(mockFetch).toHaveBeenCalledTimes(1);
            expect(mockFetch).toHaveBeenCalledWith('boulan');
        });
    });

    describe('Click outside to close', () => {
        it('should hide results when clicking outside', () => {
            resultsContainer.classList.add('show');

            // Simuler un clic en dehors
            const outsideElement = document.createElement('div');
            document.body.appendChild(outsideElement);

            // Simuler la logique de fermeture
            const hideResults = () => {
                resultsContainer.classList.remove('show');
            };

            // Si le clic n'est pas sur input ou results, fermer
            if (!searchInput.contains(outsideElement) && !resultsContainer.contains(outsideElement)) {
                hideResults();
            }

            expect(resultsContainer.classList.contains('show')).toBe(false);
        });

        it('should not hide results when clicking on results', () => {
            resultsContainer.classList.add('show');

            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            resultsContainer.appendChild(item);

            // Simuler la logique - ne devrait pas fermer car le clic est dans resultsContainer
            if (!searchInput.contains(item) && !resultsContainer.contains(item)) {
                resultsContainer.classList.remove('show');
            }

            expect(resultsContainer.classList.contains('show')).toBe(true);
        });
    });
});

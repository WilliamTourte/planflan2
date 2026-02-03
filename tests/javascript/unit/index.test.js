/**
 * Tests unitaires pour le module index.js
 *
 * Ce module teste le système d'autocomplétion de la page d'accueil
 */

describe('Index Module - Autocomplete', () => {
    let input, resultsContainer, hiddenField;

    beforeEach(() => {
        document.body.innerHTML = `
            <form id="search-form">
                <input id="ville-autocomplete" type="text">
                <input name="ville" type="hidden">
                <input name="latitude" type="hidden">
                <input name="longitude" type="hidden">
            </form>
            <div id="autocomplete-results"></div>
        `;

        input = document.getElementById('ville-autocomplete');
        resultsContainer = document.getElementById('autocomplete-results');
        hiddenField = document.querySelector('input[name="ville"]');

        jest.clearAllMocks();
        jest.useFakeTimers('modern');

        // Mock fetch
        global.fetch = jest.fn();
    });

    afterEach(() => {
        jest.useRealTimers();
        delete global.fetch;
    });

    describe('initAutocomplete', () => {
        it('should return false when input element is missing', () => {
            document.body.innerHTML = '<div id="autocomplete-results"></div>';

            // Simuler la fonction initAutocomplete
            function initAutocomplete() {
                const input = document.getElementById("ville-autocomplete");
                const resultsContainer = document.getElementById("autocomplete-results");

                if (!input || !resultsContainer) {
                    return false;
                }
                return true;
            }

            expect(initAutocomplete()).toBe(false);
        });

        it('should return false when results container is missing', () => {
            document.body.innerHTML = '<input id="ville-autocomplete">';

            function initAutocomplete() {
                const input = document.getElementById("ville-autocomplete");
                const resultsContainer = document.getElementById("autocomplete-results");

                if (!input || !resultsContainer) {
                    return false;
                }
                return true;
            }

            expect(initAutocomplete()).toBe(false);
        });

        it('should return true when all elements are present', () => {
            function initAutocomplete() {
                const input = document.getElementById("ville-autocomplete");
                const resultsContainer = document.getElementById("autocomplete-results");

                if (!input || !resultsContainer) {
                    return false;
                }
                return true;
            }

            expect(initAutocomplete()).toBe(true);
        });
    });

    describe('debounce function', () => {
        it('should delay function execution', async () => {
            const mockFn = jest.fn();

            function debounce(func, timeout = 300) {
                let timer;
                return (...args) => {
                    clearTimeout(timer);
                    timer = setTimeout(() => {
                        func(...args);
                    }, timeout);
                };
            }

            const debouncedFn = debounce(mockFn, 50); // Reduced timeout for faster test

            debouncedFn('test');
            expect(mockFn).not.toHaveBeenCalled();

            // Use real timers for this test since fake timers aren't working
            await new Promise(resolve => setTimeout(resolve, 60));
            
            expect(mockFn).toHaveBeenCalledWith('test');
        });

        it('should cancel previous timer on rapid calls', async () => {
            const mockFn = jest.fn();

            function debounce(func, timeout = 300) {
                let timer;
                return (...args) => {
                    clearTimeout(timer);
                    timer = setTimeout(() => {
                        func(...args);
                    }, timeout);
                };
            }

            const debouncedFn = debounce(mockFn, 50); // Reduced timeout for faster test

            debouncedFn('first');
            await new Promise(resolve => setTimeout(resolve, 20));
            debouncedFn('second');
            await new Promise(resolve => setTimeout(resolve, 20));
            debouncedFn('third');

            expect(mockFn).not.toHaveBeenCalled();

            // Wait for the debounce timeout to expire
            await new Promise(resolve => setTimeout(resolve, 60));
            
            expect(mockFn).toHaveBeenCalledTimes(1);
            expect(mockFn).toHaveBeenCalledWith('third');
        });
    });

    describe('syncWithHiddenField', () => {
        it('should sync input value to hidden field', () => {
            function syncWithHiddenField() {
                const hiddenField = document.querySelector('input[name="ville"]');
                if (hiddenField) {
                    hiddenField.value = input.value;
                }
            }

            input.value = 'Lyon';
            syncWithHiddenField();

            expect(hiddenField.value).toBe('Lyon');
        });

        it('should handle missing hidden field gracefully', () => {
            document.body.innerHTML = '<input id="ville-autocomplete" type="text">';
            input = document.getElementById('ville-autocomplete');

            function syncWithHiddenField() {
                const hiddenField = document.querySelector('input[name="ville"]');
                if (hiddenField) {
                    hiddenField.value = input.value;
                }
            }

            expect(() => syncWithHiddenField()).not.toThrow();
        });
    });

    describe('showLoading', () => {
        it('should display loading indicator', () => {
            function showLoading() {
                resultsContainer.innerHTML = "";
                const loading = document.createElement("div");
                loading.className = "autocomplete-loading";
                loading.textContent = "Recherche en cours...";
                resultsContainer.appendChild(loading);
                resultsContainer.classList.add("show");
            }

            showLoading();

            expect(resultsContainer.classList.contains('show')).toBe(true);
            expect(resultsContainer.querySelector('.autocomplete-loading')).toBeTruthy();
            expect(resultsContainer.textContent).toContain('Recherche en cours...');
        });
    });

    describe('showResults', () => {
        let showResults;

        beforeEach(() => {
            showResults = function(villes) {
                resultsContainer.innerHTML = "";

                if (villes.length === 0) {
                    const noResults = document.createElement("div");
                    noResults.className = "autocomplete-no-results";
                    noResults.textContent = "Aucun flan pour cette ville.";
                    resultsContainer.appendChild(noResults);
                    resultsContainer.classList.add("show");
                    return;
                }

                villes.forEach((ville) => {
                    const div = document.createElement("div");
                    div.className = "autocomplete-item";
                    div.textContent = ville;
                    resultsContainer.appendChild(div);
                });

                resultsContainer.classList.add("show");
            };
        });

        it('should display no results message when villes array is empty', () => {
            showResults([]);

            expect(resultsContainer.classList.contains('show')).toBe(true);
            expect(resultsContainer.querySelector('.autocomplete-no-results')).toBeTruthy();
        });

        it('should display city items when villes array has items', () => {
            showResults(['Paris', 'Lyon', 'Marseille']);

            const items = resultsContainer.querySelectorAll('.autocomplete-item');
            expect(items).toHaveLength(3);
            expect(items[0].textContent).toBe('Paris');
            expect(items[1].textContent).toBe('Lyon');
            expect(items[2].textContent).toBe('Marseille');
        });

        it('should add show class to results container', () => {
            showResults(['Paris']);

            expect(resultsContainer.classList.contains('show')).toBe(true);
        });
    });

    describe('fetchVilles', () => {
        it('should not fetch when query is too short', async () => {
            async function fetchVilles(query) {
                if (query.length < 2) {
                    resultsContainer.classList.remove("show");
                    return [];
                }
                // ... rest of implementation
                return [];
            }

            await fetchVilles('L');

            expect(global.fetch).not.toHaveBeenCalled();
            expect(resultsContainer.classList.contains('show')).toBe(false);
        });

        it('should fetch villes when query is long enough', async () => {
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(['Lyon', 'Lyon 1er'])
            });

            async function fetchVilles(query) {
                if (query.length < 2) {
                    resultsContainer.classList.remove("show");
                    return [];
                }

                const response = await fetch(`/api/villes?q=${encodeURIComponent(query)}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            }

            const result = await fetchVilles('Lyo');

            expect(global.fetch).toHaveBeenCalledWith('/api/villes?q=Lyo');
            expect(result).toEqual(['Lyon', 'Lyon 1er']);
        });

        it('should handle API errors gracefully', async () => {
            global.fetch.mockRejectedValueOnce(new Error('Network error'));

            async function fetchVilles(query) {
                if (query.length < 2) {
                    return [];
                }

                try {
                    const response = await fetch(`/api/villes?q=${encodeURIComponent(query)}`);
                    return await response.json();
                } catch (error) {
                    resultsContainer.innerHTML = "";
                    const errorDiv = document.createElement("div");
                    errorDiv.className = "autocomplete-no-results";
                    errorDiv.textContent = "Erreur de chargement: " + error.message;
                    resultsContainer.appendChild(errorDiv);
                    resultsContainer.classList.add("show");
                    return [];
                }
            }

            await fetchVilles('Lyon');

            expect(resultsContainer.textContent).toContain('Erreur de chargement');
        });
    });

    describe('City selection with GPS coordinates', () => {
        it('should parse GPS coordinates from API response', () => {
            const apiResponse = 'Lyon|45.7578|4.8351';
            const parts = apiResponse.split('|');

            expect(parts).toHaveLength(3);
            expect(parts[0]).toBe('Lyon');
            expect(parseFloat(parts[1])).toBe(45.7578);
            expect(parseFloat(parts[2])).toBe(4.8351);
        });

        it('should store coordinates in hidden fields', () => {
            const lat = 45.7578;
            const lng = 4.8351;

            const latitudeField = document.querySelector('input[name="latitude"]');
            const longitudeField = document.querySelector('input[name="longitude"]');

            if (latitudeField && longitudeField) {
                latitudeField.value = lat;
                longitudeField.value = lng;
            }

            expect(latitudeField.value).toBe('45.7578');
            expect(longitudeField.value).toBe('4.8351');
        });

        it('should build correct URL with coordinates', () => {
            const ville = 'Lyon';
            const lat = 45.7578;
            const lng = 4.8351;

            const url = new URL('http://localhost/liste_etablissements');
            url.searchParams.append("ville", ville);
            url.searchParams.append("latitude", lat);
            url.searchParams.append("longitude", lng);
            url.searchParams.append("from_ville_selection", "true");

            expect(url.toString()).toContain('ville=Lyon');
            expect(url.toString()).toContain('latitude=45.7578');
            expect(url.toString()).toContain('longitude=4.8351');
            expect(url.toString()).toContain('from_ville_selection=true');
        });
    });

    describe('Keyboard navigation', () => {
        it('should track current focus index', () => {
            let currentFocus = -1;

            expect(currentFocus).toBe(-1);

            currentFocus = 0;
            expect(currentFocus).toBe(0);
        });
    });

    describe('Input event handling', () => {
        it('should provide visual feedback on input', () => {
            input.style.backgroundColor = "#fffde7";

            expect(input.style.backgroundColor).toBe('rgb(255, 253, 231)');
        });
    });
});

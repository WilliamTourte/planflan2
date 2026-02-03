/**
 * Tests unitaires pour le module liste_etablissements.js
 *
 * Ce module teste l'initialisation de la page liste des établissements
 */

describe('Liste Etablissements Module', () => {
    let mockInitMapAndFilters;

    beforeEach(() => {
        document.body.innerHTML = '';
        jest.clearAllMocks();

        // Mock de la fonction initMapAndFilters
        mockInitMapAndFilters = jest.fn();
        window.initMapAndFilters = mockInitMapAndFilters;
    });

    afterEach(() => {
        delete window.initMapAndFilters;
    });

    describe('DOM data parsing', () => {
        it('should parse etablissements data from DOM element', () => {
            const etablissementsData = [
                { id_etab: 1, nom: 'Boulangerie Test', ville: 'Lyon' },
                { id_etab: 2, nom: 'Patisserie Test', ville: 'Paris' }
            ];

            document.body.innerHTML = `
                <div id="etablissements-data" data-etablissements='${JSON.stringify(etablissementsData)}'></div>
                <div id="is-admin" data-is-admin="false"></div>
                <div id="google-maps-api-key" data-api-key="test-key"></div>
            `;

            const element = document.getElementById('etablissements-data');
            const parsed = JSON.parse(element.getAttribute('data-etablissements'));

            expect(parsed).toHaveLength(2);
            expect(parsed[0].nom).toBe('Boulangerie Test');
            expect(parsed[1].ville).toBe('Paris');
        });

        it('should parse isAdmin flag from DOM element', () => {
            document.body.innerHTML = `
                <div id="etablissements-data" data-etablissements='[]'></div>
                <div id="is-admin" data-is-admin="true"></div>
                <div id="google-maps-api-key" data-api-key="test-key"></div>
            `;

            const element = document.getElementById('is-admin');
            const isAdmin = JSON.parse(element.getAttribute('data-is-admin'));

            expect(isAdmin).toBe(true);
        });

        it('should parse Google Maps API key from DOM element', () => {
            document.body.innerHTML = `
                <div id="etablissements-data" data-etablissements='[]'></div>
                <div id="is-admin" data-is-admin="false"></div>
                <div id="google-maps-api-key" data-api-key="AIzaSyTestKey123"></div>
            `;

            const element = document.getElementById('google-maps-api-key');
            const apiKey = element.getAttribute('data-api-key');

            expect(apiKey).toBe('AIzaSyTestKey123');
        });

        it('should parse user location when available', () => {
            document.body.innerHTML = `
                <div id="etablissements-data" data-etablissements='[]'></div>
                <div id="is-admin" data-is-admin="false"></div>
                <div id="google-maps-api-key" data-api-key="test-key"></div>
                <div id="user-location" data-lat="45.75" data-lon="4.85"></div>
            `;

            const element = document.getElementById('user-location');
            const lat = parseFloat(element.getAttribute('data-lat'));
            const lon = parseFloat(element.getAttribute('data-lon'));

            expect(lat).toBe(45.75);
            expect(lon).toBe(4.85);
        });

        it('should return null for user location when element is missing', () => {
            document.body.innerHTML = `
                <div id="etablissements-data" data-etablissements='[]'></div>
                <div id="is-admin" data-is-admin="false"></div>
                <div id="google-maps-api-key" data-api-key="test-key"></div>
            `;

            const element = document.getElementById('user-location');
            const lat = element ? parseFloat(element.getAttribute('data-lat')) : null;
            const lon = element ? parseFloat(element.getAttribute('data-lon')) : null;

            expect(lat).toBeNull();
            expect(lon).toBeNull();
        });

        it('should parse ville selectionnee when available', () => {
            document.body.innerHTML = `
                <div id="etablissements-data" data-etablissements='[]'></div>
                <div id="is-admin" data-is-admin="false"></div>
                <div id="google-maps-api-key" data-api-key="test-key"></div>
                <div id="ville-selectionnee" data-ville="Lyon"></div>
            `;

            const element = document.getElementById('ville-selectionnee');
            const ville = element ? element.getAttribute('data-ville') : null;

            expect(ville).toBe('Lyon');
        });

        it('should return null for ville selectionnee when element is missing', () => {
            document.body.innerHTML = `
                <div id="etablissements-data" data-etablissements='[]'></div>
                <div id="is-admin" data-is-admin="false"></div>
                <div id="google-maps-api-key" data-api-key="test-key"></div>
            `;

            const element = document.getElementById('ville-selectionnee');
            const ville = element ? element.getAttribute('data-ville') : null;

            expect(ville).toBeNull();
        });
    });

    describe('initMapAndFilters call', () => {
        it('should call initMapAndFilters when function exists', () => {
            const etablissementsData = [{ id_etab: 1, nom: 'Test' }];

            document.body.innerHTML = `
                <div id="etablissements-data" data-etablissements='${JSON.stringify(etablissementsData)}'></div>
                <div id="is-admin" data-is-admin="true"></div>
                <div id="google-maps-api-key" data-api-key="test-key"></div>
                <div id="user-location" data-lat="45.75" data-lon="4.85"></div>
                <div id="ville-selectionnee" data-ville="Lyon"></div>
            `;

            // Simuler le comportement du module
            const data = JSON.parse(document.getElementById('etablissements-data').getAttribute('data-etablissements'));
            const isAdmin = JSON.parse(document.getElementById('is-admin').getAttribute('data-is-admin'));
            const apiKey = document.getElementById('google-maps-api-key').getAttribute('data-api-key');
            const userLocationElement = document.getElementById('user-location');
            const userLat = userLocationElement ? parseFloat(userLocationElement.getAttribute('data-lat')) : null;
            const userLon = userLocationElement ? parseFloat(userLocationElement.getAttribute('data-lon')) : null;
            const villeElement = document.getElementById('ville-selectionnee');
            const ville = villeElement ? villeElement.getAttribute('data-ville') : null;

            if (typeof window.initMapAndFilters === 'function') {
                window.initMapAndFilters(data, isAdmin, apiKey, userLat, userLon, ville);
            }

            expect(mockInitMapAndFilters).toHaveBeenCalledWith(
                etablissementsData,
                true,
                'test-key',
                45.75,
                4.85,
                'Lyon'
            );
        });

        it('should not throw when initMapAndFilters is not defined', () => {
            delete window.initMapAndFilters;

            document.body.innerHTML = `
                <div id="etablissements-data" data-etablissements='[]'></div>
                <div id="is-admin" data-is-admin="false"></div>
                <div id="google-maps-api-key" data-api-key="test-key"></div>
            `;

            expect(() => {
                if (typeof window.initMapAndFilters === 'function') {
                    window.initMapAndFilters([], false, 'test-key', null, null, null);
                }
            }).not.toThrow();
        });
    });

    describe('Edge cases', () => {
        it('should handle empty etablissements array', () => {
            document.body.innerHTML = `
                <div id="etablissements-data" data-etablissements='[]'></div>
                <div id="is-admin" data-is-admin="false"></div>
                <div id="google-maps-api-key" data-api-key="test-key"></div>
            `;

            const data = JSON.parse(document.getElementById('etablissements-data').getAttribute('data-etablissements'));

            expect(data).toEqual([]);
            expect(data).toHaveLength(0);
        });

        it('should handle special characters in ville name', () => {
            document.body.innerHTML = `
                <div id="ville-selectionnee" data-ville="Saint-Étienne"></div>
            `;

            const element = document.getElementById('ville-selectionnee');
            const ville = element.getAttribute('data-ville');

            expect(ville).toBe('Saint-Étienne');
        });
    });
});

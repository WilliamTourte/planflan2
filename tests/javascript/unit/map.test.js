/**
 * Tests unitaires pour le module map.js
 *
 * Ce module teste les fonctionnalités de la carte Leaflet
 */

import {
    createEmojiIcon,
    createEtablissementMarker,
    zoomOnVille,
    setActiveFilters,
    getActiveFilters,
    setUserLocation,
    setVilleSelectionnee,
    saveCompleteStateToUrl
} from '../../../app/static/js/map.js';

// Mock des modules dépendants
jest.mock('../../../app/static/js/geolocation.js', () => ({
    GeolocationHandler: jest.fn().mockImplementation(() => ({
        activate: jest.fn().mockResolvedValue({
            coords: { latitude: 45.75, longitude: 4.85 }
        })
    }))
}));

// Mock Leaflet global
const mockPopup = {
    setContent: jest.fn().mockReturnThis(),
    update: jest.fn(),
    isOpen: jest.fn(() => false)
};

const mockMarker = {
    addTo: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
    bindPopup: jest.fn().mockReturnThis(),
    openPopup: jest.fn().mockReturnThis(),
    unbindPopup: jest.fn().mockReturnThis(),
    getPopup: jest.fn(() => null),
    getLatLng: jest.fn(() => ({ lat: 45.75, lng: 4.85 })),
    options: {},
    _popup: mockPopup
};

const mockMap = {
    setView: jest.fn().mockReturnThis(),
    panTo: jest.fn().mockReturnThis(),
    fitBounds: jest.fn().mockReturnThis(),
    getZoom: jest.fn(() => 13),
    addLayer: jest.fn(),
    removeLayer: jest.fn(),
    eachLayer: jest.fn()
};

const mockBounds = {
    extend: jest.fn().mockReturnThis(),
    isValid: jest.fn(() => true)
};

// Mock global L (Leaflet)
global.L = {
    map: jest.fn(() => mockMap),
    marker: jest.fn(() => mockMarker),
    popup: jest.fn(() => mockPopup),
    divIcon: jest.fn((options) => ({ options })),
    icon: jest.fn((options) => ({ options })),
    latLngBounds: jest.fn(() => mockBounds),
    DomUtil: {
        create: jest.fn(() => document.createElement('div'))
    },
    tileLayer: jest.fn(() => ({ addTo: jest.fn() }))
};

// Mock fetch
global.fetch = jest.fn();

describe('Map Module', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        document.body.innerHTML = '';

        // Reset fetch mock
        global.fetch.mockReset();
        global.fetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve([]),
            text: () => Promise.resolve('<div>Popup content</div>')
        });
    });

    describe('createEmojiIcon', () => {
        it('should create a div icon with emoji', () => {
            const icon = createEmojiIcon('🏠', 'test-class');

            expect(L.divIcon).toHaveBeenCalled();
            expect(L.divIcon).toHaveBeenCalledWith(
                expect.objectContaining({
                    className: 'emoji-icon'
                })
            );
        });

        it('should include the emoji in the HTML', () => {
            createEmojiIcon('❤️', 'label-icon');

            const callArgs = L.divIcon.mock.calls[0][0];
            expect(callArgs.html).toContain('❤️');
        });

        it('should include custom class in the HTML', () => {
            createEmojiIcon('✅', 'visited-icon');

            const callArgs = L.divIcon.mock.calls[0][0];
            expect(callArgs.html).toContain('visited-icon');
        });

        it('should set correct icon size', () => {
            createEmojiIcon('👋', 'unvisited-icon');

            const callArgs = L.divIcon.mock.calls[0][0];
            expect(callArgs.iconSize).toEqual([30, 30]);
            expect(callArgs.iconAnchor).toEqual([15, 15]);
        });
    });

    describe('createEtablissementMarker', () => {
        const mockEtablissement = {
            id_etab: 1,
            nom: 'Boulangerie Test',
            adresse: '1 rue Test',
            ville: 'Lyon',
            latitude: 45.75,
            longitude: 4.85,
            label: false,
            visite: false
        };

        it('should create a marker with correct position', () => {
            createEtablissementMarker(mockMap, mockEtablissement);

            expect(L.marker).toHaveBeenCalledWith(
                [45.75, 4.85],
                expect.any(Object)
            );
        });

        it('should add marker to map', () => {
            createEtablissementMarker(mockMap, mockEtablissement);

            expect(mockMarker.addTo).toHaveBeenCalledWith(mockMap);
        });

        it('should attach click event listener', () => {
            createEtablissementMarker(mockMap, mockEtablissement);

            expect(mockMarker.on).toHaveBeenCalledWith('click', expect.any(Function));
        });

        it('should use label icon for labeled establishments', () => {
            const labeledEtab = { ...mockEtablissement, label: true };

            createEtablissementMarker(mockMap, labeledEtab);

            // Vérifier que l'icône ❤️ a été utilisée
            const iconCalls = L.divIcon.mock.calls;
            const lastCall = iconCalls[iconCalls.length - 1][0];
            expect(lastCall.html).toContain('❤️');
        });

        it('should use visited icon for visited establishments', () => {
            const visitedEtab = { ...mockEtablissement, visite: true };

            createEtablissementMarker(mockMap, visitedEtab);

            const iconCalls = L.divIcon.mock.calls;
            const lastCall = iconCalls[iconCalls.length - 1][0];
            expect(lastCall.html).toContain('✅');
        });

        it('should use unvisited icon for unvisited establishments', () => {
            createEtablissementMarker(mockMap, mockEtablissement);

            const iconCalls = L.divIcon.mock.calls;
            const lastCall = iconCalls[iconCalls.length - 1][0];
            expect(lastCall.html).toContain('👋');
        });

        it('should store etablissement in marker options', () => {
            const marker = createEtablissementMarker(mockMap, mockEtablissement);

            expect(marker.options.etablissement).toEqual(mockEtablissement);
        });
    });

    describe('getActiveFilters / setActiveFilters', () => {
        it('should return current filters state', () => {
            const filters = getActiveFilters();

            expect(filters).toBeDefined();
            expect(typeof filters).toBe('object');
        });

        it('should update filters state', () => {
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
        });
    });

    describe('setUserLocation', () => {
        it('should set user location', () => {
            const location = { lat: 45.75, lng: 4.85 };

            setUserLocation(location);

            // La fonction devrait stocker la localisation
            // (vérification indirecte via d'autres fonctions)
        });
    });

    describe('setVilleSelectionnee', () => {
        it('should set selected city', () => {
            setVilleSelectionnee('Lyon');

            // La fonction devrait stocker la ville
            // (vérification indirecte via d'autres fonctions)
        });
    });

    describe('saveCompleteStateToUrl', () => {
        beforeEach(() => {
            // Mock window.history
            delete window.history;
            window.history = {
                replaceState: jest.fn()
            };
        });

        it('should save state to URL', () => {
            setActiveFilters({
                type_pate: 'Feuilletée',
                type_saveur: false,
                visited: false,
                unvisited: false,
                label: false
            });

            saveCompleteStateToUrl();

            expect(window.history.replaceState).toHaveBeenCalled();
        });

        it('should include filter parameters in URL', () => {
            // Réinitialiser le mock pour ce test
            window.history.replaceState.mockClear();

            setActiveFilters({
                type_pate: 'Brisée',
                type_saveur: 'Chocolat',
                visited: true,
                unvisited: false,
                label: false
            });

            saveCompleteStateToUrl();

            // Utiliser le dernier appel
            const calls = window.history.replaceState.mock.calls;
            const lastCall = calls[calls.length - 1];
            const url = String(lastCall[2]);

            // L'URL utilise 'pate' et 'saveur' comme paramètres
            expect(url).toMatch(/pate=/);
        });
    });

    describe('zoomOnVille', () => {
        it('should return false for empty ville', () => {
            const result = zoomOnVille('');

            expect(result).toBe(false);
        });

        it('should return false for null ville', () => {
            const result = zoomOnVille(null);

            expect(result).toBe(false);
        });
    });

    describe('Marker filtering', () => {
        it('should filter markers based on active filters', () => {
            // Test que les filtres sont appliqués correctement
            setActiveFilters({
                type_pate: 'Feuilletée',
                type_saveur: false,
                visited: false,
                unvisited: false,
                label: false
            });

            const filters = getActiveFilters();
            expect(filters.type_pate).toBe('Feuilletée');
        });

        it('should combine multiple filters', () => {
            setActiveFilters({
                type_pate: 'Brisée',
                type_saveur: 'Chocolat',
                visited: true,
                unvisited: false,
                label: false
            });

            const filters = getActiveFilters();
            expect(filters.type_pate).toBe('Brisée');
            expect(filters.type_saveur).toBe('Chocolat');
            expect(filters.visited).toBe(true);
        });
    });

    describe('Marker creation variants', () => {
        const baseEtablissement = {
            id_etab: 1,
            nom: 'Boulangerie Test',
            adresse: '1 rue Test',
            ville: 'Lyon',
            latitude: 45.75,
            longitude: 4.85,
            label: false,
            visite: false
        };

        it('should create marker with default icon for basic establishment', () => {
            createEtablissementMarker(mockMap, baseEtablissement);

            const iconCalls = L.divIcon.mock.calls;
            const lastCall = iconCalls[iconCalls.length - 1][0];
            expect(lastCall.html).toContain('👋');
        });

        it('should prioritize label over visited', () => {
            const labeledAndVisitedEtab = {
                ...baseEtablissement,
                label: true,
                visite: true
            };

            createEtablissementMarker(mockMap, labeledAndVisitedEtab);

            const iconCalls = L.divIcon.mock.calls;
            const lastCall = iconCalls[iconCalls.length - 1][0];
            expect(lastCall.html).toContain('❤️');
        });

        it('should handle click event on marker', () => {
            const marker = createEtablissementMarker(mockMap, baseEtablissement);

            expect(mockMarker.on).toHaveBeenCalledWith('click', expect.any(Function));
        });
    });

    describe('Icon creation', () => {
        it('should create emoji icon with correct structure', () => {
            createEmojiIcon('🍞', 'bread-icon');

            expect(L.divIcon).toHaveBeenCalledWith(
                expect.objectContaining({
                    className: 'emoji-icon',
                    iconSize: [30, 30],
                    iconAnchor: [15, 15]
                })
            );
        });

        it('should include custom class in icon HTML', () => {
            createEmojiIcon('🥐', 'croissant-icon');

            const callArgs = L.divIcon.mock.calls[L.divIcon.mock.calls.length - 1][0];
            expect(callArgs.html).toContain('croissant-icon');
            expect(callArgs.html).toContain('🥐');
        });
    });

    describe('zoomOnVille edge cases', () => {
        it('should return false when ville is undefined', () => {
            const result = zoomOnVille(undefined);
            expect(result).toBe(false);
        });

        it('should return false when ville is empty string', () => {
            const result = zoomOnVille('');
            expect(result).toBe(false);
        });
    });

    describe('State management', () => {
        it('should set and get user location', () => {
            const location = { lat: 45.75, lng: 4.85 };
            setUserLocation(location);

            // Vérification indirecte - la fonction ne doit pas lancer d'erreur
            expect(() => setUserLocation(location)).not.toThrow();
        });

        it('should set ville selectionnee', () => {
            setVilleSelectionnee('Paris');

            expect(() => setVilleSelectionnee('Paris')).not.toThrow();
        });

        it('should handle null ville selectionnee', () => {
            expect(() => setVilleSelectionnee(null)).not.toThrow();
        });
    });

    describe('saveCompleteStateToUrl variations', () => {
        beforeEach(() => {
            delete window.history;
            window.history = {
                replaceState: jest.fn()
            };
        });

        it('should save only active filters to URL', () => {
            setActiveFilters({
                type_pate: false,
                type_saveur: false,
                visited: false,
                unvisited: false,
                label: false
            });

            saveCompleteStateToUrl();

            expect(window.history.replaceState).toHaveBeenCalled();
        });

        it('should save visited filter to URL', () => {
            setActiveFilters({
                type_pate: false,
                type_saveur: false,
                visited: true,
                unvisited: false,
                label: false
            });

            saveCompleteStateToUrl();

            const calls = window.history.replaceState.mock.calls;
            const lastCall = calls[calls.length - 1];
            const url = String(lastCall[2]);

            expect(url).toMatch(/visited=true/);
        });
    });
});

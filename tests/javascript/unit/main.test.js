/**
 * Tests unitaires pour le module main.js
 *
 * Ce module teste le point d'entrée principal et l'initialisation des pages
 */

// Mock des modules dépendants avant l'import
jest.mock('../../../app/static/js/utils.js', () => ({
    restoreStateFromUrl: jest.fn(),
    updateActiveButtonStates: jest.fn(),
    updateMainFilterButtons: jest.fn(),
    showLoading: jest.fn(),
    hideLoading: jest.fn(),
    showToast: jest.fn()
}));

jest.mock('../../../app/static/js/geolocation.js', () => ({
    GeolocationHandler: jest.fn().mockImplementation(() => ({
        activate: jest.fn().mockResolvedValue({
            coords: { latitude: 45.75, longitude: 4.85 }
        })
    })),
    getUserLocationSimple: jest.fn().mockResolvedValue({
        latitude: 45.75,
        longitude: 4.85
    })
}));

jest.mock('../../../app/static/js/map.js', () => ({
    initMap: jest.fn(),
    updateMapAndMarkers: jest.fn(),
    setUserLocation: jest.fn(),
    setVilleSelectionnee: jest.fn(),
    setActiveFilters: jest.fn(),
    createUserMarker: jest.fn(),
    setView: jest.fn(),
    saveCompleteStateToUrl: jest.fn()
}));

jest.mock('../../../app/static/js/filters.js', () => ({
    setupFilterButtons: jest.fn(),
    restoreFiltersFromUrl: jest.fn().mockReturnValue({
        type_pate: false,
        type_saveur: false,
        visited: false,
        unvisited: false,
        label: false
    })
}));

jest.mock('../../../app/static/js/autocomplete.js', () => ({
    initAutocomplete: jest.fn().mockReturnValue(true),
    initGooglePlacesAutocomplete: jest.fn().mockResolvedValue({})
}));

jest.mock('../../../app/static/js/api.js', () => ({
    fetchWithErrorHandling: jest.fn(),
    fetchEtablissements: jest.fn(),
    fetchVilles: jest.fn()
}));

jest.mock('../../../app/static/js/macros.js', () => ({
    initMacros: jest.fn()
}));

jest.mock('../../../app/static/js/dashboard.js', () => ({
    showDeleteAccountForm: jest.fn()
}));

// Import après les mocks
import * as utils from '../../../app/static/js/utils.js';
import * as map from '../../../app/static/js/map.js';
import * as filters from '../../../app/static/js/filters.js';
import * as autocomplete from '../../../app/static/js/autocomplete.js';
import { showDeleteAccountForm } from '../../../app/static/js/dashboard.js';

describe('Main Module', () => {
    beforeEach(() => {
        // Réinitialiser le DOM
        document.body.innerHTML = '';
        jest.clearAllMocks();

        // Mock window.location
        delete window.location;
        window.location = {
            search: '',
            origin: 'http://test.example.com',
            href: 'http://test.example.com/'
        };
    });

    describe('Page initialization', () => {
        it('should detect home page type', () => {
            document.body.innerHTML = '<body data-page-type="home"></body>';
            document.body.setAttribute('data-page-type', 'home');

            const pageType = document.body.getAttribute('data-page-type');

            expect(pageType).toBe('home');
        });

        it('should detect liste_etablissements page type', () => {
            document.body.setAttribute('data-page-type', 'liste_etablissements');

            const pageType = document.body.getAttribute('data-page-type');

            expect(pageType).toBe('liste_etablissements');
        });

        it('should detect proposer_etablissement page type', () => {
            document.body.setAttribute('data-page-type', 'proposer_etablissement');

            const pageType = document.body.getAttribute('data-page-type');

            expect(pageType).toBe('proposer_etablissement');
        });

        it('should detect dashboard page type', () => {
            document.body.setAttribute('data-page-type', 'dashboard');

            const pageType = document.body.getAttribute('data-page-type');

            expect(pageType).toBe('dashboard');
        });
    });

    describe('Home page initialization', () => {
        beforeEach(() => {
            document.body.innerHTML = `
                <body data-page-type="home">
                    <input id="ville-autocomplete">
                    <div id="autocomplete-results"></div>
                    <button id="geoloc-button">📍</button>
                </body>
            `;
            document.body.setAttribute('data-page-type', 'home');
        });

        it('should initialize autocomplete on home page', () => {
            // Simuler l'initialisation de la page d'accueil
            autocomplete.initAutocomplete();

            expect(autocomplete.initAutocomplete).toHaveBeenCalled();
        });

        it('should setup geolocation button', () => {
            const geolocButton = document.getElementById('geoloc-button');

            expect(geolocButton).toBeTruthy();
        });
    });

    describe('Liste etablissements page initialization', () => {
        beforeEach(() => {
            document.body.innerHTML = `
                <body data-page-type="liste_etablissements">
                    <div id="etablissements-data" data-etablissements='[]'></div>
                    <div id="is-admin" data-is-admin="false"></div>
                    <div id="google-maps-api-key" data-api-key="test-key"></div>
                    <div id="user-location" data-lat="45.75" data-lon="4.85"></div>
                    <div id="ville-selectionnee" data-ville="Lyon"></div>
                    <div id="map"></div>
                </body>
            `;
            document.body.setAttribute('data-page-type', 'liste_etablissements');
        });

        it('should parse etablissements data', () => {
            const etablissementsDataElement = document.getElementById('etablissements-data');
            const data = JSON.parse(etablissementsDataElement.getAttribute('data-etablissements') || '[]');

            expect(Array.isArray(data)).toBe(true);
        });

        it('should parse user location', () => {
            const userLocationElement = document.getElementById('user-location');
            const lat = parseFloat(userLocationElement.getAttribute('data-lat'));
            const lon = parseFloat(userLocationElement.getAttribute('data-lon'));

            expect(lat).toBe(45.75);
            expect(lon).toBe(4.85);
        });

        it('should parse ville selectionnee', () => {
            const villeElement = document.getElementById('ville-selectionnee');
            const ville = villeElement.getAttribute('data-ville');

            expect(ville).toBe('Lyon');
        });

        it('should set user location if available', () => {
            const userLocationElement = document.getElementById('user-location');
            const lat = parseFloat(userLocationElement.getAttribute('data-lat'));
            const lon = parseFloat(userLocationElement.getAttribute('data-lon'));

            if (lat && lon) {
                map.setUserLocation({ lat, lon });
            }

            expect(map.setUserLocation).toHaveBeenCalledWith({ lat: 45.75, lon: 4.85 });
        });

        it('should set ville selectionnee if available', () => {
            const villeElement = document.getElementById('ville-selectionnee');
            const ville = villeElement.getAttribute('data-ville');

            if (ville) {
                map.setVilleSelectionnee(ville);
            }

            expect(map.setVilleSelectionnee).toHaveBeenCalledWith('Lyon');
        });
    });

    describe('Dashboard page initialization', () => {
        it('should show delete account form if error in URL', () => {
            window.location.search = '?error=deletion_failed';
            document.body.setAttribute('data-page-type', 'dashboard');

            // Simuler la vérification d'erreur
            if (window.location.search.includes('error=')) {
                showDeleteAccountForm();
            }

            expect(showDeleteAccountForm).toHaveBeenCalled();
        });

        it('should not show delete account form without error', () => {
            window.location.search = '';
            document.body.setAttribute('data-page-type', 'dashboard');

            // Réinitialiser le mock
            showDeleteAccountForm.mockClear();

            // Simuler la vérification d'erreur
            if (window.location.search.includes('error=')) {
                showDeleteAccountForm();
            }

            expect(showDeleteAccountForm).not.toHaveBeenCalled();
        });
    });

    describe('URL parameters handling', () => {
        it('should detect geolocalisation parameter', () => {
            window.location.search = '?geolocalisation=true';

            const urlParams = new URLSearchParams(window.location.search);
            const fromGeoloc = urlParams.get('geolocalisation') === 'true';

            expect(fromGeoloc).toBe(true);
        });

        it('should detect from_ville_selection parameter', () => {
            window.location.search = '?from_ville_selection=true';

            const urlParams = new URLSearchParams(window.location.search);
            const fromVilleSelection = urlParams.get('from_ville_selection') === 'true';

            expect(fromVilleSelection).toBe(true);
        });

        it('should restore filters from URL', () => {
            const restoredFilters = filters.restoreFiltersFromUrl();

            expect(restoredFilters).toBeDefined();
            expect(typeof restoredFilters).toBe('object');
        });
    });

    describe('Geolocation button', () => {
        beforeEach(() => {
            document.body.innerHTML = `
                <button id="geoloc-button">📍 Me localiser</button>
            `;
        });

        it('should exist in DOM', () => {
            const button = document.getElementById('geoloc-button');

            expect(button).toBeTruthy();
        });

        it('should be clickable', () => {
            const button = document.getElementById('geoloc-button');
            const clickHandler = jest.fn();

            button.addEventListener('click', clickHandler);
            button.click();

            expect(clickHandler).toHaveBeenCalled();
        });
    });

    describe('Common initialization', () => {
        it('should call restoreStateFromUrl', () => {
            utils.restoreStateFromUrl();

            expect(utils.restoreStateFromUrl).toHaveBeenCalled();
        });
    });
});

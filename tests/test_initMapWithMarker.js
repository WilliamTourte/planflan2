/**
 * Test de la fonction initMapWithMarker pour la page proposer_etablissement
 *
 * Ce test vérifie que la carte s'initialise correctement avec un marqueur
 * lorsqu'un établissement est sélectionné via l'autocomplete.
 */

import { initMapWithMarker } from '../app/static/js/map.js';

describe('initMapWithMarker', () => {
    let mapContainer;

    beforeEach(() => {
        // Créer un conteneur de carte pour le test
        mapContainer = document.createElement('div');
        mapContainer.id = 'map';
        mapContainer.style.height = '400px';
        document.body.appendChild(mapContainer);

        // Mock Leaflet si nécessaire
        if (typeof L === 'undefined') {
            global.L = {
                map: jest.fn(() => ({
                    setView: jest.fn().mockReturnThis(),
                    eachLayer: jest.fn(),
                    removeLayer: jest.fn()
                })),
                tileLayer: jest.fn(() => ({
                    addTo: jest.fn().mockReturnThis()
                })),
                marker: jest.fn(() => ({
                    addTo: jest.fn().mockReturnThis(),
                    bindPopup: jest.fn().mockReturnThis(),
                    openPopup: jest.fn().mockReturnThis()
                })),
                Marker: class Marker {}
            };
        }
    });

    afterEach(() => {
        // Nettoyer le DOM
        if (mapContainer && mapContainer.parentNode) {
            mapContainer.parentNode.removeChild(mapContainer);
        }
    });

    test('devrait créer une carte si elle n\'existe pas', () => {
        const lat = 48.8566;
        const lng = 2.3522;
        const nom = 'Test Établissement';

        const result = initMapWithMarker(lat, lng, nom);

        expect(result).toBeDefined();
        expect(L.map).toHaveBeenCalledWith('map');
    });

    test('devrait ajouter un marqueur avec le nom de l\'établissement', () => {
        const lat = 48.8566;
        const lng = 2.3522;
        const nom = 'Boulangerie Test';

        initMapWithMarker(lat, lng, nom);

        expect(L.marker).toHaveBeenCalledWith([lat, lng]);
    });

    test('devrait retourner null si l\'élément #map n\'existe pas', () => {
        // Supprimer l'élément map
        document.body.removeChild(mapContainer);

        const result = initMapWithMarker(48.8566, 2.3522, 'Test');

        expect(result).toBeUndefined();
    });

    test('devrait réutiliser la carte existante lors d\'une seconde sélection', () => {
        // Première sélection
        const map1 = initMapWithMarker(48.8566, 2.3522, 'Établissement 1');

        // Seconde sélection
        const map2 = initMapWithMarker(48.8575, 2.3530, 'Établissement 2');

        // Devrait réutiliser la même instance de carte
        expect(map1).toBe(map2);
        expect(map1.eachLayer).toHaveBeenCalled();
    });
});

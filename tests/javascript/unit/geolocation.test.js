/**
 * Tests unitaires pour le module geolocation.js
 *
 * Ce module teste les fonctionnalités de géolocalisation
 */

import { GeolocationHandler, getUserLocationSimple } from '../../../app/static/js/geolocation.js';

// Mock des modules dépendants
jest.mock('../../../app/static/js/utils.js', () => ({
    showLoading: jest.fn(),
    hideLoading: jest.fn(),
    showToast: jest.fn()
}));

// Mock Leaflet
const mockMap = {
    setView: jest.fn(),
    getZoom: jest.fn(() => 13),
    removeLayer: jest.fn(),
    addLayer: jest.fn()
};

const mockMarker = {
    setLatLng: jest.fn().mockReturnThis(),
    addTo: jest.fn().mockReturnThis(),
    remove: jest.fn().mockReturnThis(),
    bindPopup: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis()
};

const mockCircle = {
    setLatLng: jest.fn().mockReturnThis(),
    setRadius: jest.fn().mockReturnThis(),
    addTo: jest.fn().mockReturnThis(),
    remove: jest.fn().mockReturnThis()
};

// Mock global L (Leaflet)
global.L = {
    marker: jest.fn(() => mockMarker),
    circle: jest.fn(() => mockCircle),
    divIcon: jest.fn(() => ({})),
    icon: jest.fn(() => ({}))
};

describe('Geolocation Module', () => {
    let originalNavigator;

    beforeEach(() => {
        jest.clearAllMocks();

        // Sauvegarder et mocker navigator.geolocation
        originalNavigator = global.navigator;

        Object.defineProperty(global, 'navigator', {
            value: {
                geolocation: {
                    getCurrentPosition: jest.fn(),
                    watchPosition: jest.fn(),
                    clearWatch: jest.fn()
                }
            },
            writable: true
        });
    });

    afterEach(() => {
        // Restaurer navigator
        Object.defineProperty(global, 'navigator', {
            value: originalNavigator,
            writable: true
        });
    });

    describe('GeolocationHandler', () => {
        describe('constructor', () => {
            it('should create instance with default options', () => {
                const handler = new GeolocationHandler(mockMap);

                expect(handler.map).toBe(mockMap);
                expect(handler.options.defaultZoom).toBe(14);
                expect(handler.options.maxAccuracyRadius).toBe(1000);
            });

            it('should accept custom options', () => {
                const handler = new GeolocationHandler(mockMap, {
                    defaultZoom: 16,
                    maxAccuracyRadius: 500
                });

                expect(handler.options.defaultZoom).toBe(16);
                expect(handler.options.maxAccuracyRadius).toBe(500);
            });

            it('should initialize with null markers', () => {
                const handler = new GeolocationHandler(mockMap);

                expect(handler.userMarker).toBeNull();
                expect(handler.userCircle).toBeNull();
            });
        });

        describe('activate', () => {
            it('should reject if geolocation is not supported', async () => {
                Object.defineProperty(global, 'navigator', {
                    value: { geolocation: null },
                    writable: true
                });

                const handler = new GeolocationHandler(mockMap);

                await expect(handler.activate()).rejects.toThrow(
                    "La géolocalisation n'est pas supportée"
                );
            });

            it('should call getCurrentPosition when activated', () => {
                const handler = new GeolocationHandler(mockMap);

                handler.activate();

                expect(navigator.geolocation.getCurrentPosition).toHaveBeenCalled();
            });

            it('should resolve with position on success', async () => {
                const mockPosition = {
                    coords: {
                        latitude: 45.75,
                        longitude: 4.85,
                        accuracy: 100
                    }
                };

                navigator.geolocation.getCurrentPosition.mockImplementation(
                    (success) => success(mockPosition)
                );

                const handler = new GeolocationHandler(mockMap);
                const result = await handler.activate();

                expect(result).toEqual(mockPosition);
            });

            it('should center map on user position', async () => {
                const mockPosition = {
                    coords: {
                        latitude: 45.75,
                        longitude: 4.85,
                        accuracy: 100
                    }
                };

                navigator.geolocation.getCurrentPosition.mockImplementation(
                    (success) => success(mockPosition)
                );

                const handler = new GeolocationHandler(mockMap);
                await handler.activate();

                expect(mockMap.setView).toHaveBeenCalledWith(
                    [45.75, 4.85],
                    14
                );
            });

            it('should reject on geolocation error', async () => {
                const mockError = {
                    code: 1,
                    message: 'Permission denied'
                };

                navigator.geolocation.getCurrentPosition.mockImplementation(
                    (success, error) => error(mockError)
                );

                const handler = new GeolocationHandler(mockMap);

                await expect(handler.activate()).rejects.toEqual(mockError);
            });
        });

        describe('error handling', () => {
            it('should handle PERMISSION_DENIED error', async () => {
                const mockError = { code: 1, message: 'Permission denied' };

                navigator.geolocation.getCurrentPosition.mockImplementation(
                    (success, error) => error(mockError)
                );

                const handler = new GeolocationHandler(mockMap);

                try {
                    await handler.activate();
                } catch (e) {
                    expect(e.code).toBe(1);
                }
            });

            it('should handle POSITION_UNAVAILABLE error', async () => {
                const mockError = { code: 2, message: 'Position unavailable' };

                navigator.geolocation.getCurrentPosition.mockImplementation(
                    (success, error) => error(mockError)
                );

                const handler = new GeolocationHandler(mockMap);

                try {
                    await handler.activate();
                } catch (e) {
                    expect(e.code).toBe(2);
                }
            });

            it('should handle TIMEOUT error', async () => {
                const mockError = { code: 3, message: 'Timeout' };

                navigator.geolocation.getCurrentPosition.mockImplementation(
                    (success, error) => error(mockError)
                );

                const handler = new GeolocationHandler(mockMap);

                try {
                    await handler.activate();
                } catch (e) {
                    expect(e.code).toBe(3);
                }
            });
        });
    });

    describe('getUserLocationSimple', () => {
        it('should return a promise', () => {
            navigator.geolocation.getCurrentPosition.mockImplementation(
                (success) => success({
                    coords: { latitude: 45.75, longitude: 4.85 }
                })
            );

            const result = getUserLocationSimple();

            expect(result).toBeInstanceOf(Promise);
        });

        it('should resolve with position object on success', async () => {
            const mockPosition = {
                coords: { latitude: 45.75, longitude: 4.85 }
            };

            navigator.geolocation.getCurrentPosition.mockImplementation(
                (success) => success(mockPosition)
            );

            const result = await getUserLocationSimple();

            // La fonction retourne l'objet position complet
            expect(result.coords.latitude).toBe(45.75);
            expect(result.coords.longitude).toBe(4.85);
        });

        it('should reject if geolocation not supported', async () => {
            Object.defineProperty(global, 'navigator', {
                value: { geolocation: null },
                writable: true
            });

            await expect(getUserLocationSimple()).rejects.toThrow();
        });

        it('should reject on geolocation error', async () => {
            // Restaurer navigator.geolocation pour ce test
            Object.defineProperty(global, 'navigator', {
                value: {
                    geolocation: {
                        getCurrentPosition: jest.fn((success, error) =>
                            error(new Error('Geolocation failed'))
                        )
                    }
                },
                writable: true
            });

            await expect(getUserLocationSimple()).rejects.toThrow();
        });
    });

    describe('accuracy circle', () => {
        it('should create user marker on successful geolocation', async () => {
            const mockPosition = {
                coords: {
                    latitude: 45.75,
                    longitude: 4.85,
                    accuracy: 100 // Dans la limite du maxAccuracyRadius
                }
            };

            navigator.geolocation.getCurrentPosition.mockImplementation(
                (success) => success(mockPosition)
            );

            const handler = new GeolocationHandler(mockMap);
            await handler.activate();

            // Vérifier que le marker a été créé
            expect(L.marker).toHaveBeenCalled();
            expect(mockMarker.addTo).toHaveBeenCalledWith(mockMap);
        });

        it('should call bindPopup on user marker', async () => {
            const mockPosition = {
                coords: {
                    latitude: 45.75,
                    longitude: 4.85,
                    accuracy: 100
                }
            };

            navigator.geolocation.getCurrentPosition.mockImplementation(
                (success) => success(mockPosition)
            );

            const handler = new GeolocationHandler(mockMap);
            await handler.activate();

            // Vérifier que bindPopup a été appelé
            expect(mockMarker.bindPopup).toHaveBeenCalled();
        });
    });
});

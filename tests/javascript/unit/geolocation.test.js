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

        it('should create accuracy circle when accuracy is valid', async () => {
            const mockPosition = {
                coords: {
                    latitude: 45.75,
                    longitude: 4.85,
                    accuracy: 500 // Moins que maxAccuracyRadius de 1000
                }
            };

            navigator.geolocation.getCurrentPosition.mockImplementation(
                (success) => success(mockPosition)
            );

            const handler = new GeolocationHandler(mockMap);
            await handler.activate();

            // Vérifier que le cercle a été créé
            expect(L.circle).toHaveBeenCalled();
        });

        it('should not create accuracy circle when accuracy exceeds max', async () => {
            // Reset le mock de L.circle pour ce test
            L.circle.mockClear();

            const mockPosition = {
                coords: {
                    latitude: 45.75,
                    longitude: 4.85,
                    accuracy: 2000 // Plus que maxAccuracyRadius de 1000
                }
            };

            navigator.geolocation.getCurrentPosition.mockImplementation(
                (success) => success(mockPosition)
            );

            const handler = new GeolocationHandler(mockMap);
            await handler.activate();

            // Le cercle ne devrait pas être créé
            expect(L.circle).not.toHaveBeenCalled();
        });
    });

    describe('clear method', () => {
        it('should remove user marker when clear is called', async () => {
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

            handler.clear();

            expect(mockMap.removeLayer).toHaveBeenCalled();
            expect(handler.userMarker).toBeNull();
        });

        it('should handle clear when no markers exist', () => {
            const handler = new GeolocationHandler(mockMap);

            expect(() => handler.clear()).not.toThrow();
        });
    });

    describe('calculateDistance static method', () => {
        it('should calculate distance between two points', () => {
            // Distance entre Paris et Lyon (environ 400km)
            const distance = GeolocationHandler.calculateDistance(
                48.8566, 2.3522,  // Paris
                45.7640, 4.8357   // Lyon
            );

            // La distance devrait être environ 400km (avec une marge d'erreur)
            expect(distance).toBeGreaterThan(350);
            expect(distance).toBeLessThan(450);
        });

        it('should return 0 for same location', () => {
            const distance = GeolocationHandler.calculateDistance(
                45.75, 4.85,
                45.75, 4.85
            );

            expect(distance).toBe(0);
        });
    });

    describe('_toRad static method', () => {
        it('should convert degrees to radians', () => {
            const radians = GeolocationHandler._toRad(180);

            expect(radians).toBeCloseTo(Math.PI, 5);
        });

        it('should handle 0 degrees', () => {
            const radians = GeolocationHandler._toRad(0);

            expect(radians).toBe(0);
        });

        it('should handle 90 degrees', () => {
            const radians = GeolocationHandler._toRad(90);

            expect(radians).toBeCloseTo(Math.PI / 2, 5);
        });
    });

    describe('update marker position', () => {
        it('should update existing marker position on subsequent calls', async () => {
            const mockPosition1 = {
                coords: { latitude: 45.75, longitude: 4.85, accuracy: 100 }
            };
            const mockPosition2 = {
                coords: { latitude: 45.76, longitude: 4.86, accuracy: 100 }
            };

            navigator.geolocation.getCurrentPosition
                .mockImplementationOnce((success) => success(mockPosition1))
                .mockImplementationOnce((success) => success(mockPosition2));

            const handler = new GeolocationHandler(mockMap);
            await handler.activate();
            await handler.activate();

            // Le marqueur devrait être mis à jour, pas recréé
            expect(mockMarker.setLatLng).toHaveBeenCalled();
        });
    });
});

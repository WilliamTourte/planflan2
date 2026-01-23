// Configuration globale pour les tests Jest
import '@testing-library/jest-dom';

// Mock des fonctions globales qui pourraient être utilisées
global.showToast = jest.fn();
global.showLoading = jest.fn();
global.hideLoading = jest.fn();

// Configuration pour les tests avec DOM
beforeEach(() => {
  // Configurer jsdom avec les propriétés nécessaires
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  });
  
  // Mock pour la géolocalisation
  global.navigator.geolocation = {
    getCurrentPosition: jest.fn(),
    watchPosition: jest.fn(),
    clearWatch: jest.fn(),
  };
});

// Mock pour les modules ES6 qui pourraient être importés
jest.mock('fetch-mock', () => {
  const originalModule = jest.requireActual('fetch-mock');
  return {
    ...originalModule,
    default: originalModule,
  };
});

// Mock des fonctions globales qui pourraient être utilisées
global.showToast = jest.fn();
global.showLoading = jest.fn();
global.hideLoading = jest.fn();

// Configuration pour les tests avec DOM
beforeEach(() => {
  // Configurer jsdom avec les propriétés nécessaires
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  });
  
  // Mock pour la géolocalisation
  global.navigator.geolocation = {
    getCurrentPosition: jest.fn(),
    watchPosition: jest.fn(),
    clearWatch: jest.fn(),
  };
});

// Mock pour les modules ES6 qui pourraient être importés
jest.mock('fetch-mock', () => {
  const originalModule = jest.requireActual('fetch-mock');
  return {
    ...originalModule,
    default: originalModule,
  };
});
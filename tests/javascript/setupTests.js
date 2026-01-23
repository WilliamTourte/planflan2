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

// Configuration pour fetch-mock
import fetchMock from 'fetch-mock';

// Configurer fetch-mock pour les tests
global.fetchMock = fetchMock;

// Activer fetch-mock avant les tests
beforeAll(() => {
  if (fetchMock.config) {
    fetchMock.config.overwriteRoutes = false;
  }
});

// Nettoyer après les tests
afterAll(() => {
  if (typeof fetchMock.restore === 'function') {
    fetchMock.restore();
  }
});

// Mock pour les modules ES6 qui pourraient être importés
jest.mock('fetch-mock', () => {
  const originalModule = jest.requireActual('fetch-mock');
  return {
    ...originalModule,
    default: originalModule,
  };
});

// Configuration supplémentaire pour les tests
global.console = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
};

// Mock pour HTMLFormElement.prototype.submit qui n'est pas implémenté dans jsdom
beforeEach(() => {
  if (typeof HTMLFormElement !== 'undefined') {
    HTMLFormElement.prototype.submit = jest.fn(function() {
      // Simuler la soumission du formulaire
      const event = new Event('submit', { cancelable: true });
      this.dispatchEvent(event);
      if (!event.defaultPrevented) {
        // Si le formulaire n'est pas annulé, on peut simuler la navigation
        // ou juste logger pour les tests
        console.log('Form submitted:', this.action, this.method);
      }
    });
  }
});
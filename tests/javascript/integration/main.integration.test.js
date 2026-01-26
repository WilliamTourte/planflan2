/**
 * Tests d'intégration pour le module main.js
 * Vérifie l'interaction entre les différents modules
 */

import * as main from '../../../app/static/js/main.js';
import * as utils from '../../../app/static/js/utils.js';
import * as api from '../../../app/static/js/api.js';
import * as autocomplete from '../../../app/static/js/autocomplete.js';
import { initGeolocButton } from '../../../app/static/js/main.js';

describe('Main Module Integration', () => {
  beforeEach(() => {
    // Configurer le DOM pour les tests
    document.body.innerHTML = `
      <div data-page-type="home">
        <input id="ville-autocomplete">
        <div id="autocomplete-results"></div>
        <button id="geoloc-button">Géolocalisation</button>
        <form>
          <input name="ville" type="hidden">
          <input name="latitude" type="hidden">
          <input name="longitude" type="hidden">
        </form>
      </div>
    `;
    
    // Configurer window.location pour JSDOM (utiliser le mock existant de setupTests)
    window.location.href = 'http://localhost/home';
    window.location.origin = 'http://localhost';
    window.location.hostname = 'localhost';
    window.location.pathname = '/home';
    window.location.search = '';
    window.location.hash = '';
    
    // Mock des fonctions globales
    global.showToast = jest.fn();
    global.showLoading = jest.fn();
    global.hideLoading = jest.fn();
    
    // Mock de la géolocalisation
    global.navigator.geolocation = {
      getCurrentPosition: jest.fn((success) => {
        success({
          coords: {
            latitude: 48.8566,
            longitude: 2.3522
          }
        });
      }),
      watchPosition: jest.fn(),
      clearWatch: jest.fn()
    };
  });

  describe('Page Initialization', () => {
    it('should initialize home page correctly', () => {
      // Simuler le chargement du DOM
      document.dispatchEvent(new Event('DOMContentLoaded'));
      
      // Vérifier que l'autocomplete est initialisé
      const autocompleteInitialized = autocomplete.initAutocomplete();
      expect(autocompleteInitialized).toBe(true);
      
      // Vérifier que le bouton de géolocalisation est présent
      const geolocButton = document.getElementById('geoloc-button');
      expect(geolocButton).not.toBeNull();
    });

    it('should handle missing elements gracefully', () => {
      // Supprimer les éléments requis
      document.body.innerHTML = '<div data-page-type="home"></div>';
      
      // Vérifier que l'initialisation ne crash pas
      const autocompleteInitialized = autocomplete.initAutocomplete();
      expect(autocompleteInitialized).toBe(false);
    });
  });

  describe('Geolocation Integration', () => {
    it('should handle geolocation button click', async () => {
      // Initialiser le bouton de géolocalisation
      initGeolocButton();
      
      // Simuler le clic sur le bouton de géolocalisation
      const geolocButton = document.getElementById('geoloc-button');
      const clickEvent = new Event('click');
      geolocButton.dispatchEvent(clickEvent);
      
      // Attendre que la promesse de géolocalisation se résolve
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Vérifier que la géolocalisation a été appelée
      expect(navigator.geolocation.getCurrentPosition).toHaveBeenCalled();
      
      // Vérifier que les champs de latitude/longitude sont mis à jour
      const latitudeField = document.querySelector('input[name="latitude"]');
      const longitudeField = document.querySelector('input[name="longitude"]');
      
      // Note: Dans le test, la redirection est empêchée, donc les champs devraient être mis à jour
      expect(latitudeField.value).toBe('48.8566');
      expect(longitudeField.value).toBe('2.3522');
    });

    it('should handle geolocation errors', async () => {
      // Initialiser le bouton de géolocalisation
      initGeolocButton();
      
      // Configurer un mock d'erreur
      global.navigator.geolocation.getCurrentPosition = jest.fn((success, error) => {
        error({
          code: 1, // PERMISSION_DENIED
          message: 'Permission refusée'
        });
      });
      
      // Simuler le clic sur le bouton
      const geolocButton = document.getElementById('geoloc-button');
      const clickEvent = new Event('click');
      geolocButton.dispatchEvent(clickEvent);
      
      // Attendre que la promesse d'erreur se résolve
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Vérifier que l'erreur est affichée
      expect(showToast).toHaveBeenCalledWith('Erreur de géolocalisation: Permission refusée', 'error');
    });
  });

  describe('Module Interactions', () => {
    it('should verify module exports are available', () => {
      // Vérifier que les modules exportent les fonctions attendues
      expect(typeof utils.debounce).toBe('function');
      expect(typeof utils.showLoading).toBe('function');
      expect(typeof utils.hideLoading).toBe('function');
      expect(typeof utils.showToast).toBe('function');
      
      expect(typeof api.fetchWithErrorHandling).toBe('function');
      expect(typeof api.fetchEtablissements).toBe('function');
      expect(typeof api.fetchVilles).toBe('function');
      
      expect(typeof autocomplete.initAutocomplete).toBe('function');
    });

    it('should verify global exports for backward compatibility', () => {
      // Importer le module main.js pour déclencher les exports globaux
      try {
        require('../../../app/static/js/main.js');
      } catch (error) {
        console.log('Module main.js déjà chargé ou erreur de chargement:', error.message);
      }
      
      // Vérifier que les exports globaux sont disponibles
      expect(typeof window.utils).toBe('object');
      expect(typeof window.api).toBe('object');
      expect(typeof window.autocomplete).toBe('object');
    });
  });
});
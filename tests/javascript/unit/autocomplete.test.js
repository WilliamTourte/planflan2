/**
 * Tests unitaires pour le module autocomplete.js
 */

import { initAutocomplete } from '../../../app/static/js/autocomplete.js';
import fetchMock from 'fetch-mock';

describe('Autocomplete Module', () => {
  let input, resultsContainer;

  beforeEach(() => {
    // Configurer le DOM pour les tests
    document.body.innerHTML = `
      <input id="ville-autocomplete">
      <div id="autocomplete-results"></div>
      <form>
        <input name="ville" type="hidden">
      </form>
    `;
    
    input = document.getElementById("ville-autocomplete");
    resultsContainer = document.getElementById("autocomplete-results");
    
    fetchMock.reset();
    fetchMock.catch(500);
  });

  afterEach(() => {
    fetchMock.restore();
  });

  describe('initAutocomplete', () => {
    it('should return false when elements are missing', () => {
      document.body.innerHTML = '';
      const result = initAutocomplete();
      expect(result).toBe(false);
    });

    it('should return true when elements are present', () => {
      const result = initAutocomplete();
      expect(result).toBe(true);
    });

    it('should initialize event listeners', () => {
      initAutocomplete();
      
      // Vérifier que les event listeners sont ajoutés
      const inputEventListeners = input._events ? input._events.input : [];
      expect(inputEventListeners.length).toBeGreaterThan(0);
    });
  });

  describe('Autocomplete functionality', () => {
    it('should show results when typing', async () => {
      // Mock de la réponse API
      fetchMock.get('/api/villes?q=Par', ['Paris', 'Paris 1er']);
      
      initAutocomplete();
      
      // Simuler la saisie utilisateur
      input.value = 'Par';
      const event = new Event('input');
      input.dispatchEvent(event);
      
      // Attendre que la requête soit traitée
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Vérifier que les résultats sont affichés
      expect(resultsContainer.classList.contains('show')).toBe(true);
      expect(resultsContainer.children.length).toBe(2);
    });

    it('should handle API errors gracefully', async () => {
      // Mock d'une erreur API
      fetchMock.get('/api/villes?q=Error', 500);
      
      initAutocomplete();
      
      // Simuler la saisie utilisateur
      input.value = 'Error';
      const event = new Event('input');
      input.dispatchEvent(event);
      
      // Attendre que la requête soit traitée
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Vérifier que l'erreur est affichée
      expect(resultsContainer.classList.contains('show')).toBe(true);
      expect(resultsContainer.textContent).toContain('Erreur de chargement');
    });

    it('should sync with hidden field', () => {
      initAutocomplete();
      
      // Simuler la saisie utilisateur
      input.value = 'Test Ville';
      const event = new Event('input');
      input.dispatchEvent(event);
      
      // Vérifier que le champ caché est synchronisé
      const hiddenField = document.querySelector('input[name="ville"]');
      expect(hiddenField.value).toBe('Test Ville');
    });
  });

  describe('Result selection', () => {
    it('should handle city selection', async () => {
      // Mock de la réponse API avec coordonnées GPS
      fetchMock.get('/api/villes?q=Paris', ['Paris']);
      fetchMock.get('/api/villes?q=Paris&with_gps=true', ['Paris|48.8566|2.3522']);
      
      initAutocomplete();
      
      // Simuler la saisie et la sélection
      input.value = 'Paris';
      const inputEvent = new Event('input');
      input.dispatchEvent(inputEvent);
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Cliquer sur le premier résultat
      const firstResult = resultsContainer.firstChild;
      const clickEvent = new Event('click');
      firstResult.dispatchEvent(clickEvent);
      
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // Vérifier que le champ est mis à jour
      expect(input.value).toBe('Paris');
      const hiddenField = document.querySelector('input[name="ville"]');
      expect(hiddenField.value).toBe('Paris');
    });
  });
});
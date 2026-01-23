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
    
    // Configurer fetchMock correctement
    if (typeof fetchMock === 'function') {
      fetchMock.reset();
      fetchMock.catch(500);
    } else if (typeof fetchMock === 'object' && fetchMock.mockReset) {
      fetchMock.mockReset();
      fetchMock.mockResponse(JSON.stringify({}), { status: 500 });
    }
  });

  afterEach(() => {
    if (typeof fetchMock === 'function' && typeof fetchMock.restore === 'function') {
      fetchMock.restore();
    }
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
      const addEventListenerSpy = jest.spyOn(input, 'addEventListener');
      initAutocomplete();
      
      // Vérifier que les event listeners sont ajoutés
      expect(addEventListenerSpy).toHaveBeenCalled();
      expect(addEventListenerSpy).toHaveBeenCalledWith('input', expect.any(Function));
      
      addEventListenerSpy.mockRestore();
    });
  });

  describe('Autocomplete functionality', () => {
    it('should show results when typing', async () => {
      // Configurer le mock de fetch
      if (typeof fetchMock === 'function') {
        fetchMock.mockResponseOnce(JSON.stringify(['Paris', 'Paris 1er']), { status: 200 });
      } else if (typeof fetchMock === 'object' && fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify(['Paris', 'Paris 1er']), { status: 200 });
      } else {
        // Mock global fetch si fetchMock n'est pas disponible
        global.fetch = jest.fn(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(['Paris', 'Paris 1er'])
          })
        );
      }
      
      initAutocomplete();
      
      // Simuler la saisie utilisateur
      input.value = 'Par';
      const event = new Event('input');
      input.dispatchEvent(event);
      
      // Attendre que la requête soit traitée (debounce est à 300ms par défaut)
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Vérifier que les résultats sont affichés
      expect(resultsContainer.classList.contains('show')).toBe(true);
      expect(resultsContainer.children.length).toBe(2);
    });

    it('should handle API errors gracefully', async () => {
      // Configurer le mock d'erreur API
      if (typeof fetchMock === 'function') {
        fetchMock.mockResponseOnce(JSON.stringify({ error: 'Internal Server Error' }), { status: 500 });
      } else if (typeof fetchMock === 'object' && fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify({ error: 'Internal Server Error' }), { status: 500 });
      } else {
        // Mock global fetch pour erreur
        global.fetch = jest.fn(() =>
          Promise.resolve({
            ok: false,
            status: 500,
            json: () => Promise.resolve({ error: 'Internal Server Error' })
          })
        );
      }
      
      initAutocomplete();
      
      // Simuler la saisie utilisateur
      input.value = 'Error';
      const event = new Event('input');
      input.dispatchEvent(event);
      
      // Attendre que la requête soit traitée (debounce est à 300ms par défaut)
      await new Promise(resolve => setTimeout(resolve, 500));
      
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
      // Configurer les mocks de fetch
      if (typeof fetchMock === 'function') {
        fetchMock.mockResponseOnce(JSON.stringify(['Paris']), { status: 200 });
        fetchMock.mockResponseOnce(JSON.stringify(['Paris|48.8566|2.3522']), { status: 200 });
      } else if (typeof fetchMock === 'object' && fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify(['Paris']), { status: 200 });
        fetchMock.mockResponseOnce(JSON.stringify(['Paris|48.8566|2.3522']), { status: 200 });
      } else {
        // Mock global fetch
        let callCount = 0;
        global.fetch = jest.fn(() => {
          callCount++;
          if (callCount === 1) {
            return Promise.resolve({
              ok: true,
              json: () => Promise.resolve(['Paris'])
            });
          } else {
            return Promise.resolve({
              ok: true,
              json: () => Promise.resolve(['Paris|48.8566|2.3522'])
            });
          }
        });
      }
      
      // Mock pour empêcher la soumission du formulaire dans le test
      const originalSubmit = HTMLFormElement.prototype.submit;
      HTMLFormElement.prototype.submit = jest.fn(function() {
        console.log('Form submission prevented in test');
      });
      
      initAutocomplete();
      
      // Simuler la saisie et la sélection
      input.value = 'Paris';
      const inputEvent = new Event('input');
      input.dispatchEvent(inputEvent);
      
      // Attendre que la requête soit traitée (debounce est à 300ms par défaut)
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Cliquer sur le premier résultat
      const firstResult = resultsContainer.firstChild;
      const clickEvent = new Event('click');
      firstResult.dispatchEvent(clickEvent);
      
      // Attendre que le clic soit traité
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Vérifier que le champ est mis à jour
      // Note: Le champ input est mis à jour avec juste "Paris" par le clic
      // mais le champ caché peut contenir le format complet
      expect(input.value).toBe('Paris');
      const hiddenField = document.querySelector('input[name="ville"]');
      expect(hiddenField.value).toBe('Paris');
      
      // Restaurer le submit original
      if (originalSubmit) {
        HTMLFormElement.prototype.submit = originalSubmit;
      }
    });
  });
});
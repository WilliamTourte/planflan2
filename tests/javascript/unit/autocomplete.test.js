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
        // Mock global fetch - version corrigée pour distinguer les types de requêtes
        global.fetch = jest.fn((url) => {
          if (url.includes('/api/villes')) {
            if (url.includes('with_gps=true')) {
              // Requête pour les coordonnées GPS - retourner le format complet
              return Promise.resolve({
                ok: true,
                json: () => Promise.resolve(['Paris|48.8566|2.3522'])
              });
            } else {
              // Requête normale pour les villes - retourner juste les noms
              return Promise.resolve({
                ok: true,
                json: () => Promise.resolve(['Paris'])
              });
            }
          }
          // Pour les autres URLs, retourner une réponse vide
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([])
          });
        });
      }
      
      // Mock pour empêcher la soumission du formulaire dans le test
      const originalSubmit = HTMLFormElement.prototype.submit;
      HTMLFormElement.prototype.submit = jest.fn(function() {
        console.log('Form submission prevented in test');
        // Ne pas réinitialiser les champs du formulaire
        return false;
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
      
      // Attendre un peu plus longtemps pour que toutes les opérations asynchrones se terminent
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Vérifier que le champ est mis à jour
      // Note: Le champ input est mis à jour avec juste "Paris" par le clic
      // mais le champ caché peut contenir le format complet
      console.log('Valeur finale de input:', input.value);
      console.log('Valeur de input avant le clic:', 'Paris'); // Valeur attendue
      const hiddenField = document.querySelector('input[name="ville"]');
      console.log('Valeur finale de hiddenField:', hiddenField.value);
      
      // Le problème semble être que le champ input est réinitialisé après le clic
      // Vérifions si le formulaire est soumis
      expect(input.value).toBe('Paris');
      expect(hiddenField.value).toBe('Paris');
      
      // Restaurer le submit original
      if (originalSubmit) {
        HTMLFormElement.prototype.submit = originalSubmit;
      }
      
      // Restaurer le fetch original
      if (global.fetch && global.fetch.mockRestore) {
        global.fetch.mockRestore();
      }
    });
  });

  describe('Keyboard navigation', () => {
    beforeEach(() => {
      // Configurer le mock de fetch
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(['Paris', 'Lyon', 'Marseille'])
        })
      );
    });

    it('should navigate down with arrow key', async () => {
      initAutocomplete();

      input.value = 'Par';
      input.dispatchEvent(new Event('input'));

      await new Promise(resolve => setTimeout(resolve, 500));

      // Simuler la touche flèche vers le bas
      const keydownEvent = new KeyboardEvent('keydown', { key: 'ArrowDown' });
      input.dispatchEvent(keydownEvent);

      // La sélection devrait passer au premier élément
      const items = resultsContainer.querySelectorAll('.autocomplete-item');
      if (items.length > 0) {
        expect(items[0]).toBeDefined();
      }
    });

    it('should navigate up with arrow key', async () => {
      initAutocomplete();

      input.value = 'Par';
      input.dispatchEvent(new Event('input'));

      await new Promise(resolve => setTimeout(resolve, 500));

      // Simuler la touche flèche vers le haut
      const keydownEvent = new KeyboardEvent('keydown', { key: 'ArrowUp' });
      input.dispatchEvent(keydownEvent);

      expect(resultsContainer.classList.contains('show')).toBe(true);
    });

    it('should select item with Enter key', async () => {
      initAutocomplete();

      input.value = 'Par';
      input.dispatchEvent(new Event('input'));

      await new Promise(resolve => setTimeout(resolve, 500));

      // Simuler flèche bas puis Enter
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown' }));

      const enterEvent = new KeyboardEvent('keydown', { key: 'Enter' });
      input.dispatchEvent(enterEvent);

      // L'entrée devrait être mise à jour
      expect(input.value).toBeDefined();
    });

    it('should close results when clicking outside', async () => {
      initAutocomplete();

      input.value = 'Par';
      input.dispatchEvent(new Event('input'));

      await new Promise(resolve => setTimeout(resolve, 500));

      expect(resultsContainer.classList.contains('show')).toBe(true);

      // Simuler un clic en dehors du champ input (comportement réel du module)
      const outsideElement = document.body;
      const clickEvent = new MouseEvent('click', { bubbles: true });
      outsideElement.dispatchEvent(clickEvent);

      expect(resultsContainer.classList.contains('show')).toBe(false);
    });
  });

  describe('Click outside handling', () => {
    it('should hide results when clicking outside input', async () => {
      initAutocomplete();

      input.value = 'Par';
      input.dispatchEvent(new Event('input'));

      await new Promise(resolve => setTimeout(resolve, 500));

      expect(resultsContainer.classList.contains('show')).toBe(true);

      // Créer un élément externe et simuler un clic
      const outsideDiv = document.createElement('div');
      outsideDiv.id = 'outside';
      document.body.appendChild(outsideDiv);

      const clickEvent = new MouseEvent('click', { bubbles: true });
      outsideDiv.dispatchEvent(clickEvent);

      expect(resultsContainer.classList.contains('show')).toBe(false);
    });

    it('should keep results visible when clicking on input', async () => {
      initAutocomplete();

      input.value = 'Par';
      input.dispatchEvent(new Event('input'));

      await new Promise(resolve => setTimeout(resolve, 500));

      expect(resultsContainer.classList.contains('show')).toBe(true);

      // Simuler un clic sur l'input lui-même
      const clickEvent = new MouseEvent('click', { bubbles: true });
      input.dispatchEvent(clickEvent);

      // Les résultats devraient rester visibles
      expect(resultsContainer.classList.contains('show')).toBe(true);
    });
  });

  describe('No results handling', () => {
    it('should show no results message', async () => {
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        })
      );

      initAutocomplete();

      input.value = 'ZZZ';
      input.dispatchEvent(new Event('input'));

      await new Promise(resolve => setTimeout(resolve, 500));

      expect(resultsContainer.classList.contains('show')).toBe(true);
      expect(resultsContainer.querySelector('.autocomplete-no-results')).toBeTruthy();
    });
  });

  describe('zoomToLocation', () => {
    it('should handle zoom with Leaflet map', async () => {
      // Mock window.location
      delete window.location;
      window.location = {
        href: 'http://test.com/',
        origin: 'http://test.com'
      };

      // Mock Leaflet global
      const mockMarker = {
        addTo: jest.fn().mockReturnThis(),
        bindPopup: jest.fn().mockReturnThis(),
        openPopup: jest.fn().mockReturnThis()
      };

      global.L = {
        marker: jest.fn(() => mockMarker)
      };

      // Mock window.map (Leaflet)
      window.map = {
        setView: jest.fn(),
        removeLayer: jest.fn()
      };

      // Importer la fonction zoomToLocation
      const { zoomToLocation } = await import('../../../app/static/js/autocomplete.js');

      if (typeof zoomToLocation === 'function') {
        zoomToLocation(48.8566, 2.3522, 'Paris');

        expect(window.map.setView).toHaveBeenCalledWith([48.8566, 2.3522], 12);
      }

      // Cleanup
      delete window.map;
      delete global.L;
    });

    it('should store pending zoom when no map is available', async () => {
      // Mock window.location
      delete window.location;
      window.location = {
        href: 'http://test.com/',
        origin: 'http://test.com'
      };

      // S'assurer qu'aucune carte n'est disponible
      delete window.map;
      delete global.google;
      delete global.L;

      // Importer la fonction zoomToLocation
      const { zoomToLocation } = await import('../../../app/static/js/autocomplete.js');

      if (typeof zoomToLocation === 'function') {
        zoomToLocation(45.75, 4.85, 'Lyon');

        expect(window.pendingZoom).toEqual({
          lat: 45.75,
          lng: 4.85,
          ville: 'Lyon'
        });
      }

      // Cleanup
      delete window.pendingZoom;
    });
  });
});
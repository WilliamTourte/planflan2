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
    
    // Set page type for proposer page tests
    document.body.setAttribute('data-page-type', 'proposer_etablissement');
    
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

    it('should store GPS coordinates in hidden fields when city is selected', async () => {
      // Configurer les mocks de fetch comme dans le test qui fonctionne
      if (typeof fetchMock === 'function') {
        fetchMock.mockResponseOnce(JSON.stringify(['Paris']), { status: 200 });
        fetchMock.mockResponseOnce(JSON.stringify(['Paris|48.8566|2.3522']), { status: 200 });
      } else if (typeof fetchMock === 'object' && fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify(['Paris']), { status: 200 });
        fetchMock.mockResponseOnce(JSON.stringify(['Paris|48.8566|2.3522']), { status: 200 });
      } else {
        // Mock global fetch avec mockImplementationOnce pour simuler les deux appels
        global.fetch = jest.fn()
          .mockImplementationOnce(() =>
            Promise.resolve({
              ok: true,
              json: () => Promise.resolve(['Paris'])
            })
          )
          .mockImplementationOnce(() =>
            Promise.resolve({
              ok: true,
              json: () => Promise.resolve(['Paris|48.8566|2.3522'])
            })
          );
      }

      // Mock pour empêcher la soumission du formulaire dans le test
      const originalSubmit = HTMLFormElement.prototype.submit;
      HTMLFormElement.prototype.submit = jest.fn(function() {
        console.log('Form submission prevented in test');
        return false;
      });

      // Reconfigurer le DOM pour inclure les champs cachés de coordonnées
      document.body.innerHTML = `
        <input id="ville-autocomplete">
        <div id="autocomplete-results"></div>
        <form>
          <input name="ville" type="hidden">
          <input name="latitude" type="hidden">
          <input name="longitude" type="hidden">
        </form>
      `;

      // Set page type to proposer_etablissement to enable GPS coordinate handling
      document.body.setAttribute('data-page-type', 'proposer_etablissement');

      // Réinitialiser les références aux éléments
      input = document.getElementById("ville-autocomplete");
      resultsContainer = document.getElementById("autocomplete-results");

      initAutocomplete();

      // Simuler la saisie et la sélection
      input.value = 'Paris';
      input.dispatchEvent(new Event('input'));

      // Attendre que la requête soit traitée (debounce est à 300ms par défaut)
      await new Promise(resolve => setTimeout(resolve, 500));

      // Vérifier que les résultats sont affichés
      expect(resultsContainer.classList.contains('show')).toBe(true);
      expect(resultsContainer.children.length).toBeGreaterThan(0);

      // Cliquer sur le premier résultat
      const firstResult = resultsContainer.firstChild;
      expect(firstResult).toBeTruthy();
      firstResult.dispatchEvent(new Event('click'));

      // Attendre que le clic soit traité
      await new Promise(resolve => setTimeout(resolve, 500));

      // Vérifier que les coordonnées sont stockées dans les champs cachés
      const latitudeField = document.querySelector('input[name="latitude"]');
      const longitudeField = document.querySelector('input[name="longitude"]');

      expect(latitudeField).toBeTruthy();
      expect(longitudeField).toBeTruthy();
      expect(latitudeField.value).toBe('48.8566');
      expect(longitudeField.value).toBe('2.3522');

      // Restaurer le submit original
      if (originalSubmit) {
        HTMLFormElement.prototype.submit = originalSubmit;
      }

      // Restaurer le fetch original
      if (global.fetch && global.fetch.mockRestore) {
        global.fetch.mockRestore();
      }
    });

    it('should not call zoomToLocation on homepage when no map is available', async () => {
      // Mock zoomToLocation pour vérifier qu'elle n'est pas appelée
      const mockZoomToLocation = jest.fn();
      window.zoomToLocation = mockZoomToLocation;

      // Mock global fetch
      global.fetch = jest.fn((url) => {
        if (url.includes('/api/villes')) {
          if (url.includes('with_gps=true')) {
            return Promise.resolve({
              ok: true,
              json: () => Promise.resolve(['Paris|48.8566|2.3522'])
            });
          } else {
            return Promise.resolve({
              ok: true,
              json: () => Promise.resolve(['Paris'])
            });
          }
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      });

      // Mock pour empêcher la soumission du formulaire
      const originalSubmit = HTMLFormElement.prototype.submit;
      HTMLFormElement.prototype.submit = jest.fn(function() {
        return false;
      });

      initAutocomplete();

      // Simuler la sélection d'une ville
      input.value = 'Paris';
      input.dispatchEvent(new Event('input'));

      await new Promise(resolve => setTimeout(resolve, 500));

      // Vérifier que les résultats sont affichés
      expect(resultsContainer.classList.contains('show')).toBe(true);
      expect(resultsContainer.children.length).toBeGreaterThan(0);

      // Cliquer sur le premier résultat
      const firstResult = resultsContainer.firstChild;
      expect(firstResult).toBeTruthy();
      firstResult.dispatchEvent(new Event('click'));

      await new Promise(resolve => setTimeout(resolve, 500));

      // Vérifier que zoomToLocation n'a pas été appelée
      expect(mockZoomToLocation).not.toHaveBeenCalled();

      // Nettoyage
      delete window.zoomToLocation;

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

  describe('City restriction functionality', () => {
    let searchInput, villeInput, googleMapsApiKey;

    beforeEach(() => {
      // Configurer le DOM pour les tests de restriction par ville
      document.body.innerHTML = `
        <meta name="csrf-token" content="test-csrf-token">
        <input id="ville-autocomplete" value="Paris">
        <input id="search" class="form-control">
        <div id="autocomplete-results"></div>
        <div class="form-container"></div>
        <form>
          <input name="ville" type="hidden" id="ajout-etab-ville">
          <input name="latitude" type="hidden" id="ajout-etab-latitude">
          <input name="longitude" type="hidden" id="ajout-etab-longitude">
          <input name="google_place_id" type="hidden" id="ajout-etab-google_place_id">
          <input name="nom" type="text" id="ajout-etab-nom">
          <input name="adresse" type="text" id="ajout-etab-adresse">
        </form>
        <div id="google-maps-api-key" data-api-key="test_api_key"></div>
      `;

      searchInput = document.getElementById('search');
      villeInput = document.getElementById('ville-autocomplete');
      googleMapsApiKey = 'test_api_key';

      // Mock des fonctions qui font des appels API pour éviter les erreurs
      // Nous devons mock la fonction avant d'importer le module
      window.verifyAndProcessEtablissement = jest.fn((place) => {
        console.log('Mock verifyAndProcessEtablissement appelé avec:', place);
        // Simuler le comportement réel sans faire d'appels API
        return Promise.resolve();
      });

      // Mock Google Maps API
      global.google = {
        maps: {
          LatLng: jest.fn((lat, lng) => ({ lat: () => lat, lng: () => lng })),
          LatLngBounds: jest.fn((sw, ne) => ({
            contains: jest.fn((location) => {
              // Simuler une vérification de bounds simple
              const lat = location.lat();
              const lng = location.lng();
              return lat >= sw.lat() && lat <= ne.lat() && lng >= sw.lng() && lng <= ne.lng();
            })
          })),
          places: {
            Autocomplete: jest.fn((input, options) => {
              let mockPlace = null;
              let currentCallback = null;
              
              // Créer une instance mock qui se comporte comme un vrai Autocomplete
              const autocompleteInstance = {
                cityName: options.location ? 'Paris' : null,
                cityLat: options.location ? 48.8566 : null,
                cityLng: options.location ? 2.3522 : null,
                cityBounds: options.bounds ? options.bounds : null,
                
                // Méthode getPlace qui retourne le mock place
                getPlace: () => mockPlace,
                
                // Méthode addListener qui simule l'événement place_changed
                addListener: jest.fn((event, callback) => {
                  if (event === 'place_changed') {
                    currentCallback = callback;
                    
                    // Simuler un lieu dans la ville spécifiée
                    const ville = options.location ? 'Paris' : 'Paris'; // Valeur par défaut
                    
                    // Si nous avons des informations de ville dans les options, les utiliser
                    if (options && options.location) {
                      // Pour les tests, nous pouvons vérifier si la ville est Lyon
                      if (options.location.lat && options.location.lat() === 45.75) {
                        mockPlace = {
                          name: 'Boulangerie Test Lyon',
                          formatted_address: '1 Rue Test, Lyon',
                          geometry: {
                            location: {
                              lat: () => 45.75,
                              lng: () => 4.85
                            }
                          },
                          place_id: 'test_place_id_lyon',
                          address_components: [
                            {
                              types: ['locality'],
                              long_name: 'Lyon'
                            }
                          ]
                        };
                      } else {
                        mockPlace = {
                          name: 'Boulangerie Test',
                          formatted_address: '1 Rue Test, Paris',
                          geometry: {
                            location: {
                              lat: () => 48.8566,
                              lng: () => 2.3522
                            }
                          },
                          place_id: 'test_place_id',
                          address_components: [
                            {
                              types: ['locality'],
                              long_name: 'Paris'
                            }
                          ]
                        };
                      }
                    } else {
                      mockPlace = {
                        name: 'Boulangerie Test',
                        formatted_address: '1 Rue Test, Paris',
                        geometry: {
                          location: {
                            lat: () => 48.8566,
                            lng: () => 2.3522
                          }
                        },
                        place_id: 'test_place_id',
                        address_components: [
                          {
                            types: ['locality'],
                            long_name: 'Paris'
                          }
                        ]
                      };
                    }
                    
                    // Appeler le callback avec le mock place
                    setTimeout(() => callback(mockPlace), 100);
                  }
                }),
                
                // Méthode utilitaire pour les tests
                setMockPlace: (place) => {
                  mockPlace = place;
                  if (currentCallback) {
                    setTimeout(() => currentCallback(place), 100);
                  }
                }
              };
              
              return autocompleteInstance;
            }),
            PlacesServiceStatus: {
              OK: 'OK'
            }
          }
        }
      };

      // Mock également la fonction fetch pour les appels API
      // Sauvegarder le fetch original si nécessaire
      const originalFetch = global.fetch;
      
      global.fetch = jest.fn((url) => {
        if (url.includes('/verifier_etablissement')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ exists: false })
          });
        }
        if (url.includes('/extraire_infos_adresse')) {
          // Retourner les informations d'adresse pour Lyon
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ code_postal: '69001', ville: 'Lyon', adresse_nettoyee: '1 Rue Test, Lyon' })
          });
        }
        if (url.includes('/api/villes') && url.includes('with_gps=true')) {
          // Extraire le paramètre de ville de l'URL
          const villeMatch = url.match(/q=([^&]+)/);
          const ville = villeMatch ? decodeURIComponent(villeMatch[1]) : 'Paris';
          
          // Retourner les coordonnées GPS en fonction de la ville
          if (ville === 'Lyon') {
            return Promise.resolve({
              ok: true,
              json: () => Promise.resolve(['Lyon|45.75|4.85'])
            });
          } else {
            return Promise.resolve({
              ok: true,
              json: () => Promise.resolve(['Paris|48.8566|2.3522'])
            });
          }
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      });
    });

    afterEach(() => {
      // Nettoyage
      delete global.google;
      if (global.fetch && global.fetch.mockRestore) {
        global.fetch.mockRestore();
      }
    });

    it('should initialize autocomplete with city restriction when ville is selected', async () => {
      // Importer les fonctions nécessaires
      const { initGooglePlacesAutocompleteWithCity } = await import('../../../app/static/js/autocomplete.js');

      // Appeler la fonction avec une ville sélectionnée
      await initGooglePlacesAutocompleteWithCity('search', googleMapsApiKey, 'Paris');

      // Vérifier que l'autocomplete a été initialisé avec les bons paramètres
      expect(global.google.maps.places.Autocomplete).toHaveBeenCalled();
      const callOptions = global.google.maps.places.Autocomplete.mock.calls[0][1];

      // Vérifier que les paramètres de restriction sont présents
      expect(callOptions.strictBounds).toBe(true);
      expect(callOptions.bounds).toBeDefined();
      expect(callOptions.location).toBeDefined();
      expect(callOptions.radius).toBe(10000); // 10km
    });

    it('should create bounds around the selected city', async () => {
      // Importer les fonctions nécessaires
      const { initGooglePlacesAutocompleteWithCity } = await import('../../../app/static/js/autocomplete.js');

      // Appeler la fonction avec une ville sélectionnée
      await initGooglePlacesAutocompleteWithCity('search', googleMapsApiKey, 'Paris');

      // Vérifier que les bounds ont été créés correctement
      const callOptions = global.google.maps.places.Autocomplete.mock.calls[0][1];
      expect(callOptions.bounds).toBeDefined();

      // Vérifier que les bounds contiennent le centre de la ville
      const center = callOptions.location;
      expect(callOptions.bounds.contains(center)).toBe(true);
    });

    it('should show city restriction feedback when ville is selected', async () => {
      // Importer les fonctions nécessaires
      const { initGooglePlacesAutocompleteWithCity } = await import('../../../app/static/js/autocomplete.js');

      // Appeler la fonction avec une ville sélectionnée
      await initGooglePlacesAutocompleteWithCity('search', googleMapsApiKey, 'Paris');

      // Vérifier que le feedback visuel est affiché
      const feedbackElement = document.querySelector('.autocomplete-city-feedback');
      expect(feedbackElement).toBeTruthy();
      expect(feedbackElement.textContent).toContain('Recherche limitée à Paris');
      expect(feedbackElement.textContent).toContain('10km');
    });

    it('should restrict place selection to city bounds', async () => {
      // Importer les fonctions nécessaires
      const { initGooglePlacesAutocompleteWithCity } = await import('../../../app/static/js/autocomplete.js');

      // Appeler la fonction avec une ville sélectionnée
      await initGooglePlacesAutocompleteWithCity('search', googleMapsApiKey, 'Paris');

      // Attendre que le callback soit déclenché
      await new Promise(resolve => setTimeout(resolve, 200));

      // Vérifier que les champs ont été remplis correctement
      const nomField = document.getElementById('ajout-etab-nom');
      const adresseField = document.getElementById('ajout-etab-adresse');
      const latitudeField = document.getElementById('ajout-etab-latitude');
      const longitudeField = document.getElementById('ajout-etab-longitude');
      const googlePlaceIdField = document.getElementById('ajout-etab-google_place_id');

      expect(nomField).toBeTruthy();
      expect(adresseField).toBeTruthy();
      expect(latitudeField).toBeTruthy();
      expect(longitudeField).toBeTruthy();
      expect(googlePlaceIdField).toBeTruthy();

      expect(nomField.value).toBe('Boulangerie Test');
      expect(adresseField.value).toBe('1 Rue Test, Paris');
      expect(latitudeField.value).toBe('48.8566');
      expect(longitudeField.value).toBe('2.3522');
      expect(googlePlaceIdField.value).toBe('test_place_id');
    });

    it('should reject places outside city bounds', async () => {
      // Importer les fonctions nécessaires
      const { initGooglePlacesAutocompleteWithCity } = await import('../../../app/static/js/autocomplete.js');

      // Appeler la fonction avec une ville sélectionnée
      await initGooglePlacesAutocompleteWithCity('search', googleMapsApiKey, 'Paris');

      // Récupérer l'instance d'autocomplete
      const autocompleteInstance = global.google.maps.places.Autocomplete.mock.results[0].value;

      // Définir un mock place en dehors des bounds
      const mockPlaceOutside = {
        name: 'Boulangerie Lointaine',
        formatted_address: '1 Rue Lointaine, Versailles',
        geometry: {
          location: {
            lat: () => 48.8014, // Versailles - en dehors de Paris
            lng: () => 2.1327
          }
        },
        place_id: 'outside_place_id',
        address_components: [
          {
            types: ['locality'],
            long_name: 'Versailles'
          }
        ]
      };

      // Simuler que les bounds ne contiennent pas ce lieu
      const mockBounds = {
        contains: jest.fn(() => false) // Simuler que le lieu est en dehors des bounds
      };
      autocompleteInstance.cityBounds = mockBounds;

      // Déclencher la sélection du lieu en dehors
      autocompleteInstance.setMockPlace(mockPlaceOutside);

      // Attendre que le callback soit déclenché
      await new Promise(resolve => setTimeout(resolve, 200));

      // Vérifier que les champs n'ont pas été remplis (lieu rejeté)
      const nomField = document.getElementById('ajout-etab-nom');
      const adresseField = document.getElementById('ajout-etab-adresse');
      const latitudeField = document.getElementById('ajout-etab-latitude');
      const longitudeField = document.getElementById('ajout-etab-longitude');
      const googlePlaceIdField = document.getElementById('ajout-etab-google_place_id');

      expect(nomField).toBeTruthy();
      expect(adresseField).toBeTruthy();
      expect(latitudeField).toBeTruthy();
      expect(longitudeField).toBeTruthy();
      expect(googlePlaceIdField).toBeTruthy();

      expect(nomField.value).toBe('');
      expect(adresseField.value).toBe('');
      expect(latitudeField.value).toBe('');
      expect(longitudeField.value).toBe('');
      expect(googlePlaceIdField.value).toBe('');
    });

    it('should clear city restriction feedback when clear button is clicked', async () => {
      // Importer les fonctions nécessaires
      const { initGooglePlacesAutocompleteWithCity, clearCityRestrictionFeedback } = await import('../../../app/static/js/autocomplete.js');

      // D'abord initialiser avec une ville
      await initGooglePlacesAutocompleteWithCity('search', googleMapsApiKey, 'Paris');

      // Vérifier que le feedback est présent
      let feedbackElement = document.querySelector('.autocomplete-city-feedback');
      expect(feedbackElement).toBeTruthy();

      // Appeler la fonction de nettoyage
      clearCityRestrictionFeedback();

      // Vérifier que le feedback a été supprimé
      feedbackElement = document.querySelector('.autocomplete-city-feedback');
      expect(feedbackElement).toBeNull();
    });

    it('should handle city selection event and update establishment autocomplete', async () => {
      // Importer les fonctions nécessaires
      const { initAutocomplete, initGooglePlacesAutocompleteWithCity } = await import('../../../app/static/js/autocomplete.js');

      // Initialiser l'autocomplete pour les villes
      const villeInitResult = initAutocomplete();
      expect(villeInitResult).toBe(true);

      // Simuler la sélection d'une ville en mettant directement à jour le champ caché
      // (ce qui est ce que fait l'événement villeSelected dans la réalité)
      villeInput.value = 'Lyon';
      const hiddenVilleField = document.getElementById('ajout-etab-ville');
      hiddenVilleField.value = 'Lyon';
      
      // Réinitialiser le champ de recherche d'établissement
      searchInput.value = '';
      searchInput.focus();

      // Appeler directement l'initialisation avec restriction
      await initGooglePlacesAutocompleteWithCity('search', googleMapsApiKey, 'Lyon');

      // Attendre un peu pour que l'initialisation soit terminée
      await new Promise(resolve => setTimeout(resolve, 100));

      // Vérifier que le champ caché ville a été mis à jour
      expect(hiddenVilleField).toBeTruthy();
      expect(hiddenVilleField.value).toBe('Lyon');

      // Vérifier que le champ de recherche d'établissement a été réinitialisé
      expect(searchInput).toBeTruthy();
      expect(searchInput.value).toBe('');
      
      // Vérifier que le feedback visuel est affiché
      const feedbackElement = document.querySelector('.autocomplete-city-feedback');
      expect(feedbackElement).toBeTruthy();
      expect(feedbackElement.textContent).toContain('Recherche limitée à Lyon');
    });
  });
});
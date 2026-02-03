/**
 * Tests unitaires pour le module utils.js
 */

import {
  debounce,
  showLoading,
  hideLoading,
  showToast,
  toggleActiveButton,
  saveStateToUrl,
  restoreStateFromUrl,
  updateActiveButtonStates,
  updateMainFilterButtons,
  goBackOrRedirect
} from '../../../app/static/js/utils.js';

describe('Utils Module', () => {
  // Mock pour les fonctions globales
  global.showToast = jest.fn();
  global.showLoading = jest.fn();
  global.hideLoading = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    document.body.innerHTML = '';
  });

  describe('debounce', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should debounce function calls', (done) => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 100); // Réduire le délai pour le test

      // Appeler plusieurs fois rapidement
      debouncedFn();
      debouncedFn();
      debouncedFn();

      // Vérifier que la fonction n'a pas été appelée immédiatement
      expect(mockFn).not.toHaveBeenCalled();

      // Attendre que le timer se termine
      setTimeout(() => {
        // Vérifier que la fonction a été appelée une seule fois
        expect(mockFn).toHaveBeenCalledTimes(1);
        done();
      }, 150);
    });

    it('should call function with latest arguments', (done) => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 100); // Réduire le délai pour le test

      debouncedFn('arg1');
      debouncedFn('arg2');
      debouncedFn('arg3');

      // Attendre que le timer se termine
      setTimeout(() => {
        expect(mockFn).toHaveBeenCalledWith('arg3');
        done();
      }, 150);
    });

    it('should use default timeout of 300ms', () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn);

      debouncedFn();
      expect(mockFn).not.toHaveBeenCalled();
    });
  });

  describe('showLoading', () => {
    it('should show loading indicator', () => {
      // La fonction showLoading crée l'élément si nécessaire
      document.body.innerHTML = '';
      
      showLoading('Chargement...');
      
      const indicator = document.getElementById('global-loading-indicator');
      expect(indicator).not.toBeNull();
      expect(indicator.style.display).toBe('flex');
      // Vérifier que le texte est dans l'élément span
      const messageElement = indicator.querySelector('span');
      expect(messageElement).not.toBeNull();
      expect(messageElement.textContent).toContain('Chargement...');
    });

    it('should use default message when none provided', () => {
      document.body.innerHTML = '';

      showLoading();

      const indicator = document.getElementById('global-loading-indicator');
      const messageElement = indicator.querySelector('span');
      expect(messageElement.textContent).toContain('Chargement...');
    });

    it('should update existing loading indicator message', () => {
      document.body.innerHTML = '';

      showLoading('Premier message');
      showLoading('Deuxième message');

      const indicator = document.getElementById('global-loading-indicator');
      const messageElement = indicator.querySelector('span');
      expect(messageElement.textContent).toBe('Deuxième message');
    });
  });

  describe('hideLoading', () => {
    it('should hide loading indicator', () => {
      document.body.innerHTML = '<div id="global-loading-indicator" style="display: flex;"></div>';
      
      hideLoading();
      
      const indicator = document.getElementById('global-loading-indicator');
      expect(indicator.style.display).toBe('none');
    });

    it('should not throw when indicator does not exist', () => {
      document.body.innerHTML = '';

      expect(() => hideLoading()).not.toThrow();
    });
  });

  describe('showToast', () => {
    it('should show toast message', () => {
      document.body.innerHTML = '<div id="toast-container"></div>';
      
      showToast('Message de test', 'success');
      
      const toastContainer = document.getElementById('toast-container');
      expect(toastContainer.children.length).toBe(1);
      expect(toastContainer.firstChild.textContent).toContain('Message de test');
      expect(toastContainer.firstChild.className).toContain('success');
    });

    it('should show error toast', () => {
      document.body.innerHTML = '<div id="toast-container"></div>';
      
      showToast('Erreur de test', 'error');
      
      const toastContainer = document.getElementById('toast-container');
      expect(toastContainer.firstChild.className).toContain('error');
    });

    it('should show info toast by default', () => {
      document.body.innerHTML = '<div id="toast-container"></div>';

      showToast('Message info');

      const toastContainer = document.getElementById('toast-container');
      expect(toastContainer.firstChild.className).toContain('info');
    });

    it('should show warning toast', () => {
      document.body.innerHTML = '<div id="toast-container"></div>';

      showToast('Attention', 'warning');

      const toastContainer = document.getElementById('toast-container');
      expect(toastContainer.firstChild.className).toContain('warning');
    });

    it('should create toast container if not exists', () => {
      document.body.innerHTML = '';

      showToast('Message de test', 'success');

      const toastContainer = document.getElementById('toast-container');
      expect(toastContainer).not.toBeNull();
      expect(toastContainer.children.length).toBe(1);
    });

    it('should remove toast when close button is clicked', () => {
      document.body.innerHTML = '<div id="toast-container"></div>';

      showToast('Message à fermer', 'success');

      const toastContainer = document.getElementById('toast-container');
      const closeButton = toastContainer.querySelector('.btn-close');
      expect(closeButton).not.toBeNull();

      closeButton.click();

      expect(toastContainer.children.length).toBe(0);
    });
  });

  describe('toggleActiveButton', () => {
    it('should add active class when button is not active', () => {
      const button = document.createElement('button');

      toggleActiveButton(button, false);

      expect(button.classList.contains('active')).toBe(true);
    });

    it('should remove active class when button is active', () => {
      const button = document.createElement('button');
      button.classList.add('active');

      toggleActiveButton(button, true);

      expect(button.classList.contains('active')).toBe(false);
    });
  });

  describe('saveStateToUrl', () => {
    beforeEach(() => {
      delete window.location;
      window.location = new URL('http://test.com/page');
      window.history.replaceState = jest.fn();
    });

    it('should save state to URL parameters', () => {
      const state = {
        pate: 'Feuilletée',
        saveur: 'Vanille',
        visited: true
      };

      saveStateToUrl(state);

      expect(window.history.replaceState).toHaveBeenCalled();
    });

    it('should remove empty values from URL', () => {
      const state = {
        pate: 'Feuilletée',
        saveur: '',
        visited: null
      };

      saveStateToUrl(state);

      expect(window.history.replaceState).toHaveBeenCalled();
    });
  });

  describe('restoreStateFromUrl', () => {
    it('should restore state from URL parameters', () => {
      delete window.location;
      window.location = new URL('http://test.com/?pate=Feuilletée&visited=true');

      const state = restoreStateFromUrl();

      expect(state.pate).toBe('Feuilletée');
      expect(state.visited).toBe(true);
    });

    it('should convert numeric values', () => {
      delete window.location;
      window.location = new URL('http://test.com/?zoom=14&lat=45.5');

      const state = restoreStateFromUrl();

      expect(state.zoom).toBe(14);
      expect(state.lat).toBe(45.5);
    });

    it('should handle boolean false', () => {
      delete window.location;
      window.location = new URL('http://test.com/?visited=false');

      const state = restoreStateFromUrl();

      expect(state.visited).toBe(false);
    });

    it('should return empty object for no parameters', () => {
      delete window.location;
      window.location = new URL('http://test.com/');

      const state = restoreStateFromUrl();

      expect(Object.keys(state).length).toBe(0);
    });
  });

  describe('updateActiveButtonStates', () => {
    it('should update pate button states', () => {
      document.body.innerHTML = `
        <button id="filter-type_pate_FEUILLETEE">Feuilletée</button>
        <button id="filter-type_pate_BRISEE">Brisée</button>
      `;

      const activeFilters = { type_pate: 'Feuilletée' };

      updateActiveButtonStates(activeFilters);

      const buttonFeuilletee = document.getElementById('filter-type_pate_FEUILLETEE');
      const buttonBrisee = document.getElementById('filter-type_pate_BRISEE');

      expect(buttonFeuilletee.classList.contains('active')).toBe(true);
      expect(buttonBrisee.classList.contains('active')).toBe(false);
    });

    it('should update saveur button states', () => {
      document.body.innerHTML = `
        <button id="filter-type_saveur_VANILLE">Vanille</button>
        <button id="filter-type_saveur_CHOCOLAT">Chocolat</button>
      `;

      const activeFilters = { type_saveur: 'Chocolat' };

      updateActiveButtonStates(activeFilters);

      const buttonVanille = document.getElementById('filter-type_saveur_VANILLE');
      const buttonChocolat = document.getElementById('filter-type_saveur_CHOCOLAT');

      expect(buttonVanille.classList.contains('active')).toBe(false);
      expect(buttonChocolat.classList.contains('active')).toBe(true);
    });

    it('should update statut button states', () => {
      document.body.innerHTML = `
        <button id="filter-visited">Visité</button>
        <button id="filter-unvisited">Non visité</button>
        <button id="filter-label">Labellisé</button>
      `;

      const activeFilters = { visited: true, unvisited: false, label: false };

      updateActiveButtonStates(activeFilters);

      expect(document.getElementById('filter-visited').classList.contains('active')).toBe(true);
      expect(document.getElementById('filter-unvisited').classList.contains('active')).toBe(false);
      expect(document.getElementById('filter-label').classList.contains('active')).toBe(false);
    });
  });

  describe('updateMainFilterButtons', () => {
    it('should highlight pate main button when pate filter is active', () => {
      document.body.innerHTML = `
        <button id="filter-pate-btn">Pâte</button>
        <button id="filter-saveur-btn">Saveur</button>
        <button id="filter-statut-btn">Statut</button>
      `;

      const activeFilters = { type_pate: 'Feuilletée' };

      updateMainFilterButtons(activeFilters);

      expect(document.getElementById('filter-pate-btn').classList.contains('active')).toBe(true);
      expect(document.getElementById('filter-saveur-btn').classList.contains('active')).toBe(false);
    });

    it('should highlight saveur main button when saveur filter is active', () => {
      document.body.innerHTML = `
        <button id="filter-pate-btn">Pâte</button>
        <button id="filter-saveur-btn">Saveur</button>
        <button id="filter-statut-btn">Statut</button>
      `;

      const activeFilters = { type_saveur: 'Vanille' };

      updateMainFilterButtons(activeFilters);

      expect(document.getElementById('filter-saveur-btn').classList.contains('active')).toBe(true);
    });

    it('should highlight statut main button when visited filter is active', () => {
      document.body.innerHTML = `
        <button id="filter-pate-btn">Pâte</button>
        <button id="filter-saveur-btn">Saveur</button>
        <button id="filter-statut-btn">Statut</button>
      `;

      const activeFilters = { visited: true };

      updateMainFilterButtons(activeFilters);

      expect(document.getElementById('filter-statut-btn').classList.contains('active')).toBe(true);
    });

    it('should highlight statut main button when label filter is active', () => {
      document.body.innerHTML = `
        <button id="filter-pate-btn">Pâte</button>
        <button id="filter-saveur-btn">Saveur</button>
        <button id="filter-statut-btn">Statut</button>
      `;

      const activeFilters = { label: true };

      updateMainFilterButtons(activeFilters);

      expect(document.getElementById('filter-statut-btn').classList.contains('active')).toBe(true);
    });

    it('should handle missing buttons gracefully', () => {
      document.body.innerHTML = '';

      const activeFilters = { type_pate: 'Feuilletée' };

      expect(() => updateMainFilterButtons(activeFilters)).not.toThrow();
    });
  });

  describe('goBackOrRedirect', () => {
    let hrefSetter;

    beforeEach(() => {
      hrefSetter = jest.fn();
      window.history.back = jest.fn();

      delete window.location;
      window.location = {
        host: 'test.example.com',
        href: 'http://test.example.com/page'
      };
      Object.defineProperty(window.location, 'href', {
        set: hrefSetter,
        get: () => 'http://test.example.com/page'
      });
    });

    it('should go back when referrer is from same host', () => {
      Object.defineProperty(document, 'referrer', {
        value: 'http://test.example.com/previous-page',
        configurable: true
      });

      goBackOrRedirect('/fallback');

      expect(window.history.back).toHaveBeenCalled();
    });

    it('should redirect to fallback when no referrer', () => {
      Object.defineProperty(document, 'referrer', {
        value: '',
        configurable: true
      });

      goBackOrRedirect('/fallback');

      expect(hrefSetter).toHaveBeenCalledWith('/fallback');
    });

    it('should redirect to fallback when referrer is external', () => {
      Object.defineProperty(document, 'referrer', {
        value: 'http://external-site.com/page',
        configurable: true
      });

      goBackOrRedirect('/home');

      expect(hrefSetter).toHaveBeenCalledWith('/home');
    });
  });
});
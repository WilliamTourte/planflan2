/**
 * Tests unitaires pour le module utils.js
 */

import { debounce, showLoading, hideLoading, showToast } from '../../../app/static/js/utils.js';

describe('Utils Module', () => {
  // Mock pour les fonctions globales
  global.showToast = jest.fn();
  global.showLoading = jest.fn();
  global.hideLoading = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('debounce', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should debounce function calls', async () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 500);

      // Appeler plusieurs fois rapidement
      debouncedFn();
      debouncedFn();
      debouncedFn();

      // Vérifier que la fonction n'a pas été appelée immédiatement
      expect(mockFn).not.toHaveBeenCalled();

      // Avancer le temps et exécuter les timers
      jest.advanceTimersByTime(500);
      await new Promise(resolve => setTimeout(resolve, 100));

      // Vérifier que la fonction a été appelée une seule fois
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should call function with latest arguments', async () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 500);

      debouncedFn('arg1');
      debouncedFn('arg2');
      debouncedFn('arg3');

      jest.advanceTimersByTime(500);
      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockFn).toHaveBeenCalledWith('arg3');
    });
  });

  describe('showLoading', () => {
    it('should show loading indicator', () => {
      document.body.innerHTML = '<div id="global-loading-indicator" style="display: none;"></div>';
      
      showLoading('Chargement...');
      
      const indicator = document.getElementById('global-loading-indicator');
      expect(indicator.style.display).toBe('flex');
      // Vérifier que le texte est dans l'élément span
      const messageElement = indicator.querySelector('span');
      expect(messageElement).not.toBeNull();
      expect(messageElement.textContent).toContain('Chargement...');
    });
  });

  describe('hideLoading', () => {
    it('should hide loading indicator', () => {
      document.body.innerHTML = '<div id="global-loading-indicator" style="display: flex;"></div>';
      
      hideLoading();
      
      const indicator = document.getElementById('global-loading-indicator');
      expect(indicator.style.display).toBe('none');
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
  });
});
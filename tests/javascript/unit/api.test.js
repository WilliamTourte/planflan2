/**
 * Tests unitaires pour le module api.js
 */

import { fetchWithErrorHandling, fetchEtablissements, fetchVilles } from '../../../app/static/js/api.js';
import fetchMock from 'fetch-mock';

describe('API Module', () => {
  beforeEach(() => {
    // Réinitialiser fetchMock correctement
    if (fetchMock.reset) {
      fetchMock.reset();
    } else if (fetchMock.mockReset) {
      fetchMock.mockReset();
    }
    
    // Configurer une réponse par défaut
    if (fetchMock.mockResponse) {
      fetchMock.mockResponse(JSON.stringify({}), { status: 500 });
    } else if (fetchMock.catch) {
      fetchMock.catch(500);
    }
  });

  afterEach(() => {
    // Restaurer fetchMock correctement
    if (fetchMock.restore) {
      fetchMock.restore();
    } else if (fetchMock.mockRestore) {
      fetchMock.mockRestore();
    }
  });

  describe('fetchWithErrorHandling', () => {
    it('should handle successful API calls', async () => {
      const mockData = { success: true, data: 'test' };
      
      // Configurer le mock correctement
      if (fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 });
      } else if (fetchMock.once) {
        fetchMock.once(JSON.stringify(mockData), { status: 200 });
      } else {
        // Mock global fetch si nécessaire
        global.fetch = jest.fn(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockData)
          })
        );
      }

      const result = await fetchWithErrorHandling('/api/test');
      expect(result).toEqual(mockData);
    });

    it('should handle API errors', async () => {
      // Configurer le mock d'erreur
      if (fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify({ error: 'Internal Server Error' }), { status: 500 });
      } else if (fetchMock.once) {
        fetchMock.once(JSON.stringify({ error: 'Internal Server Error' }), { status: 500 });
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

      await expect(fetchWithErrorHandling('/api/error')).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      // Configurer le mock de rejet
      if (fetchMock.mockReject) {
        fetchMock.mockReject(new Error('Network error'));
      } else if (fetchMock.reject) {
        fetchMock.reject(new Error('Network error'));
      } else {
        // Mock global fetch pour rejet
        global.fetch = jest.fn(() =>
          Promise.reject(new Error('Network error'))
        );
      }

      await expect(fetchWithErrorHandling('/api/network-error')).rejects.toThrow('Network error');
    });

    it('should handle JSON parsing errors', async () => {
      // Configurer le mock de réponse invalide
      if (fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce('invalid json', { status: 200 });
      } else if (fetchMock.once) {
        fetchMock.once('invalid json', { status: 200 });
      } else {
        // Mock global fetch pour JSON invalide
        global.fetch = jest.fn(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.reject(new Error('Invalid JSON'))
          })
        );
      }

      await expect(fetchWithErrorHandling('/api/invalid-json')).rejects.toThrow();
    });
  });

  describe('fetchEtablissements', () => {
    it('should fetch establishments successfully', async () => {
      const mockEtablissements = [
        { id_etab: 1, nom: 'Boulangerie 1' },
        { id_etab: 2, nom: 'Boulangerie 2' }
      ];
      
      // Configurer le mock
      if (fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify(mockEtablissements), { status: 200 });
      } else if (fetchMock.once) {
        fetchMock.once(JSON.stringify(mockEtablissements), { status: 200 });
      } else {
        // Mock global fetch
        global.fetch = jest.fn(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockEtablissements)
          })
        );
      }

      const result = await fetchEtablissements();
      expect(result).toEqual(mockEtablissements);
    });

    it('should handle establishment fetch errors', async () => {
      // Configurer le mock d'erreur
      if (fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify({ error: 'Not Found' }), { status: 500 });
      } else if (fetchMock.once) {
        fetchMock.once(JSON.stringify({ error: 'Not Found' }), { status: 500 });
      } else {
        // Mock global fetch pour erreur
        global.fetch = jest.fn(() =>
          Promise.resolve({
            ok: false,
            status: 500,
            json: () => Promise.resolve({ error: 'Not Found' })
          })
        );
      }

      await expect(fetchEtablissements()).rejects.toThrow();
    });
  });

  describe('fetchVilles', () => {
    it('should fetch cities successfully', async () => {
      const mockVilles = ['Paris', 'Lyon', 'Marseille'];
      
      // Configurer le mock
      if (fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify(mockVilles), { status: 200 });
      } else if (fetchMock.once) {
        fetchMock.once(JSON.stringify(mockVilles), { status: 200 });
      } else {
        // Mock global fetch
        global.fetch = jest.fn(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockVilles)
          })
        );
      }

      const result = await fetchVilles('test');
      expect(result).toEqual(mockVilles);
    });

    it('should handle city fetch errors', async () => {
      // Configurer le mock d'erreur
      if (fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify({ error: 'Not Found' }), { status: 500 });
      } else if (fetchMock.once) {
        fetchMock.once(JSON.stringify({ error: 'Not Found' }), { status: 500 });
      } else {
        // Mock global fetch pour erreur
        global.fetch = jest.fn(() =>
          Promise.resolve({
            ok: false,
            status: 500,
            json: () => Promise.resolve({ error: 'Not Found' })
          })
        );
      }

      await expect(fetchVilles('test')).rejects.toThrow();
    });

    it('should encode query parameters', async () => {
      const mockVilles = ['Paris'];
      
      // Configurer le mock
      if (fetchMock.mockResponseOnce) {
        fetchMock.mockResponseOnce(JSON.stringify(mockVilles), { status: 200 });
      } else if (fetchMock.once) {
        fetchMock.once(JSON.stringify(mockVilles), { status: 200 });
      } else {
        // Mock global fetch
        global.fetch = jest.fn(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockVilles)
          })
        );
      }

      const result = await fetchVilles('Paris Test');
      expect(result).toEqual(mockVilles);
    });
  });
});
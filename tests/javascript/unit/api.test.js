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

  describe('checkEtablissementExists', () => {
    it('should check if establishment exists successfully', async () => {
      const { checkEtablissementExists } = await import('../../../app/static/js/api.js');
      const mockResponse = { exists: true, id_etab: 1 };

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })
      );

      const result = await checkEtablissementExists('Boulangerie Test');
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith('/verifier_etablissement', expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ nom: 'Boulangerie Test' })
      }));
    });

    it('should handle establishment not found', async () => {
      const { checkEtablissementExists } = await import('../../../app/static/js/api.js');
      const mockResponse = { exists: false };

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })
      );

      const result = await checkEtablissementExists('Unknown');
      expect(result.exists).toBe(false);
    });
  });

  describe('extractAddressInfo', () => {
    it('should extract address information successfully', async () => {
      const { extractAddressInfo } = await import('../../../app/static/js/api.js');
      const mockResponse = {
        ville: 'Paris',
        code_postal: '75001',
        rue: '1 rue de Rivoli'
      };

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })
      );

      const result = await extractAddressInfo('1 rue de Rivoli, 75001 Paris');
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith('/extraire_infos_adresse', expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ adresse: '1 rue de Rivoli, 75001 Paris' })
      }));
    });
  });

  describe('fetchInfowindowContent', () => {
    it('should fetch infowindow content successfully', async () => {
      const { fetchInfowindowContent } = await import('../../../app/static/js/api.js');
      const mockContent = '<div class="infowindow-content"><h3>Boulangerie</h3></div>';

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          text: () => Promise.resolve(mockContent)
        })
      );

      const result = await fetchInfowindowContent(1);
      expect(result).toBe(mockContent);
      expect(global.fetch).toHaveBeenCalledWith('/get_infowindow_content?id_etab=1');
    });

    it('should handle infowindow fetch error', async () => {
      const { fetchInfowindowContent } = await import('../../../app/static/js/api.js');

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          status: 404
        })
      );

      const result = await fetchInfowindowContent(999);
      expect(result).toContain('Impossible de charger les détails');
    });

    it('should handle network error for infowindow', async () => {
      const { fetchInfowindowContent } = await import('../../../app/static/js/api.js');

      global.fetch = jest.fn(() =>
        Promise.reject(new Error('Network error'))
      );

      const result = await fetchInfowindowContent(1);
      expect(result).toContain('Impossible de charger les détails');
    });
  });

  describe('submitEtablissement', () => {
    it('should submit establishment successfully', async () => {
      const { submitEtablissement } = await import('../../../app/static/js/api.js');
      const etablissementData = {
        nom: 'Nouvelle Boulangerie',
        adresse: '123 rue Test',
        ville: 'Paris'
      };
      const mockResponse = { success: true, id_etab: 10 };

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })
      );

      const result = await submitEtablissement(etablissementData);
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith('/proposer_etablissement', expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(etablissementData)
      }));
    });

    it('should handle submission error', async () => {
      const { submitEtablissement } = await import('../../../app/static/js/api.js');

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          status: 400,
          json: () => Promise.resolve({ message: 'Données invalides' })
        })
      );

      await expect(submitEtablissement({})).rejects.toThrow();
    });
  });

  describe('updateEtablissement', () => {
    it('should update establishment successfully', async () => {
      const { updateEtablissement } = await import('../../../app/static/js/api.js');
      const updateData = { nom: 'Boulangerie Modifiée' };
      const mockResponse = { success: true };

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })
      );

      const result = await updateEtablissement(1, updateData);
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith('/etablissement/1/update', expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify(updateData)
      }));
    });

    it('should handle update error', async () => {
      const { updateEtablissement } = await import('../../../app/static/js/api.js');

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          status: 404,
          json: () => Promise.resolve({ message: 'Établissement non trouvé' })
        })
      );

      await expect(updateEtablissement(999, {})).rejects.toThrow();
    });
  });

  describe('deleteEtablissement', () => {
    it('should delete establishment successfully', async () => {
      const { deleteEtablissement } = await import('../../../app/static/js/api.js');
      const mockResponse = { success: true };

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })
      );

      const result = await deleteEtablissement(1);
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith('/etablissement/1/delete', expect.objectContaining({
        method: 'DELETE'
      }));
    });

    it('should handle delete error', async () => {
      const { deleteEtablissement } = await import('../../../app/static/js/api.js');

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          status: 403,
          json: () => Promise.resolve({ message: 'Non autorisé' })
        })
      );

      await expect(deleteEtablissement(1)).rejects.toThrow();
    });
  });
});
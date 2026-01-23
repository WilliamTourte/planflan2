/**
 * Tests unitaires pour le module api.js
 */

import { fetchWithErrorHandling, fetchEtablissements, fetchVilles } from '../../../app/static/js/api.js';
import fetchMock from 'fetch-mock';

describe('API Module', () => {
  beforeEach(() => {
    fetchMock.reset();
    fetchMock.catch(500);
  });

  afterEach(() => {
    fetchMock.restore();
  });

  describe('fetchWithErrorHandling', () => {
    it('should handle successful API calls', async () => {
      const mockData = { success: true, data: 'test' };
      fetchMock.get('/api/test', mockData);

      const result = await fetchWithErrorHandling('/api/test');
      expect(result).toEqual(mockData);
    });

    it('should handle API errors', async () => {
      fetchMock.get('/api/error', 500);

      await expect(fetchWithErrorHandling('/api/error')).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      fetchMock.get('/api/network-error', { throws: new Error('Network error') });

      await expect(fetchWithErrorHandling('/api/network-error')).rejects.toThrow('Network error');
    });

    it('should handle JSON parsing errors', async () => {
      fetchMock.get('/api/invalid-json', 'invalid json');

      await expect(fetchWithErrorHandling('/api/invalid-json')).rejects.toThrow();
    });
  });

  describe('fetchEtablissements', () => {
    it('should fetch establishments successfully', async () => {
      const mockEtablissements = [
        { id_etab: 1, nom: 'Boulangerie 1' },
        { id_etab: 2, nom: 'Boulangerie 2' }
      ];
      fetchMock.get('/api/etablissements', mockEtablissements);

      const result = await fetchEtablissements();
      expect(result).toEqual(mockEtablissements);
    });

    it('should handle establishment fetch errors', async () => {
      fetchMock.get('/api/etablissements', 500);

      await expect(fetchEtablissements()).rejects.toThrow();
    });
  });

  describe('fetchVilles', () => {
    it('should fetch cities successfully', async () => {
      const mockVilles = ['Paris', 'Lyon', 'Marseille'];
      fetchMock.get('/api/villes?q=test', mockVilles);

      const result = await fetchVilles('test');
      expect(result).toEqual(mockVilles);
    });

    it('should handle city fetch errors', async () => {
      fetchMock.get('/api/villes?q=test', 500);

      await expect(fetchVilles('test')).rejects.toThrow();
    });

    it('should encode query parameters', async () => {
      const mockVilles = ['Paris'];
      fetchMock.get('/api/villes?q=Paris%20Test', mockVilles);

      const result = await fetchVilles('Paris Test');
      expect(result).toEqual(mockVilles);
    });
  });
});
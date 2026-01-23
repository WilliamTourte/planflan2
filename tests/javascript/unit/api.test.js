/**
 * Tests unitaires pour le module api.js
 */

import { fetchWithErrorHandling, fetchEtablissements, fetchVilles } from '../../../app/static/js/api.js';
import fetchMock from 'fetch-mock';

describe('API Module', () => {
  beforeEach(() => {
    fetchMock.mockReset();
    fetchMock.mockResponse(JSON.stringify({}), { status: 500 });
  });

  afterEach(() => {
    fetchMock.mockRestore();
  });

  describe('fetchWithErrorHandling', () => {
    it('should handle successful API calls', async () => {
      const mockData = { success: true, data: 'test' };
      fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 });

      const result = await fetchWithErrorHandling('/api/test');
      expect(result).toEqual(mockData);
    });

    it('should handle API errors', async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ error: 'Internal Server Error' }), { status: 500 });

      await expect(fetchWithErrorHandling('/api/error')).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      fetchMock.mockReject(new Error('Network error'));

      await expect(fetchWithErrorHandling('/api/network-error')).rejects.toThrow('Network error');
    });

    it('should handle JSON parsing errors', async () => {
      fetchMock.mockResponseOnce('invalid json', { status: 200 });

      await expect(fetchWithErrorHandling('/api/invalid-json')).rejects.toThrow();
    });
  });

  describe('fetchEtablissements', () => {
    it('should fetch establishments successfully', async () => {
      const mockEtablissements = [
        { id_etab: 1, nom: 'Boulangerie 1' },
        { id_etab: 2, nom: 'Boulangerie 2' }
      ];
      fetchMock.mockResponseOnce(JSON.stringify(mockEtablissements), { status: 200 });

      const result = await fetchEtablissements();
      expect(result).toEqual(mockEtablissements);
    });

    it('should handle establishment fetch errors', async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ error: 'Not Found' }), { status: 500 });

      await expect(fetchEtablissements()).rejects.toThrow();
    });
  });

  describe('fetchVilles', () => {
    it('should fetch cities successfully', async () => {
      const mockVilles = ['Paris', 'Lyon', 'Marseille'];
      fetchMock.mockResponseOnce(JSON.stringify(mockVilles), { status: 200 });

      const result = await fetchVilles('test');
      expect(result).toEqual(mockVilles);
    });

    it('should handle city fetch errors', async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ error: 'Not Found' }), { status: 500 });

      await expect(fetchVilles('test')).rejects.toThrow();
    });

    it('should encode query parameters', async () => {
      const mockVilles = ['Paris'];
      fetchMock.mockResponseOnce(JSON.stringify(mockVilles), { status: 200 });

      const result = await fetchVilles('Paris Test');
      expect(result).toEqual(mockVilles);
    });
  });
});
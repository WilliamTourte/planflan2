// Mock handlers pour les requêtes API
import { rest } from 'msw';

export const handlers = [
  // Mock pour l'API des établissements
  rest.get('/api/etablissements', (req, res, ctx) => {
    return res(
      ctx.json([
        {
          id_etab: 1,
          nom: 'Boulangerie Test',
          adresse: '1 Rue Test',
          ville: 'Paris',
          code_postal: '75001',
          latitude: 48.8566,
          longitude: 2.3522
        }
      ])
    );
  }),
  
  // Mock pour l'API des villes
  rest.get('/api/villes', (req, res, ctx) => {
    const query = req.url.searchParams.get('q');
    
    if (query === 'Paris') {
      return res(
        ctx.json(['Paris', 'Paris 1er', 'Paris 2e'])
      );
    }
    
    if (query === 'Lyon') {
      return res(
        ctx.json(['Lyon', 'Lyon 1er', 'Lyon 2e'])
      );
    }
    
    return res(
      ctx.json(['Aucun résultat'])
    );
  }),
  
  // Mock pour la vérification d'établissement
  rest.post('/verifier_etablissement', (req, res, ctx) => {
    const { nom } = req.body;
    
    if (nom === 'Boulangerie Test') {
      return res(
        ctx.json({ existe: true })
      );
    }
    
    return res(
      ctx.json({ existe: false })
    );
  }),
  
  // Mock pour l'extraction d'adresse
  rest.post('/extraire_infos_adresse', (req, res, ctx) => {
    return res(
      ctx.json({
        adresse: '1 Rue Test',
        ville: 'Paris',
        code_postal: '75001',
        latitude: 48.8566,
        longitude: 2.3522
      })
    );
  }),
  
  // Mock pour le contenu de l'infowindow
  rest.get('/get_infowindow_content', (req, res, ctx) => {
    return res(
      ctx.text('<div class="infowindow-content"><h3>Boulangerie Test</h3><p>1 Rue Test, Paris</p></div>')
    );
  })
];
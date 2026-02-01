/**
 * Test d'intégration pour vérifier que les filtres fonctionnent correctement
 * après la refactorisation
 */

// Simuler les éléments DOM nécessaires
const mockMapElement = document.createElement('div');
mockMapElement.id = 'map';
mockMapElement.style.width = '100px';
mockMapElement.style.height = '100px';
document.body.appendChild(mockMapElement);

const mockEtablissementsData = document.createElement('div');
mockEtablissementsData.id = 'etablissements-data';
mockEtablissementsData.setAttribute('data-etablissements', JSON.stringify([
    {
        id_etab: 1,
        nom: "Test Etablissement 1",
        adresse: "123 Rue Test",
        ville: "TestVille",
        latitude: 48.8566,
        longitude: 2.3522,
        visite: true,
        label: false,
        flans: [{ type_pate: "FEUILLETEE", type_saveur: "VANILLE" }]
    },
    {
        id_etab: 2,
        nom: "Test Etablissement 2",
        adresse: "456 Rue Test",
        ville: "TestVille",
        latitude: 48.8567,
        longitude: 2.3523,
        visite: false,
        label: true,
        flans: [{ type_pate: "BRISEE", type_saveur: "CHOCOLAT" }]
    }
]));
document.body.appendChild(mockEtablissementsData);

const mockIsAdmin = document.createElement('div');
mockIsAdmin.id = 'is-admin';
mockIsAdmin.setAttribute('data-is-admin', 'false');
document.body.appendChild(mockIsAdmin);

const mockGoogleMapsApiKey = document.createElement('div');
mockGoogleMapsApiKey.id = 'google-maps-api-key';
mockGoogleMapsApiKey.setAttribute('data-api-key', '');
document.body.appendChild(mockGoogleMapsApiKey);

// Simuler les boutons de filtre
const mockFilterButtons = document.createElement('div');
mockFilterButtons.id = 'filter-controls';
mockFilterButtons.innerHTML = `
    <button id="filter-all" class="btn btn-success">Tous</button>
    <button id="filter-visited" class="btn btn-success">Visité</button>
    <button id="filter-unvisited" class="btn btn-success">Non visité</button>
    <button id="filter-label" class="btn btn-success">Labellisé</button>
`;
document.body.appendChild(mockFilterButtons);

console.log('Test: Intégration des filtres après refactorisation...');

// Charger les modules
import * as map from './app/static/js/map.js';
import * as filters from './app/static/js/filters.js';

async function runTest() {
    try {
        // Initialiser la carte
        console.log('1. Initialisation de la carte...');
        map.initMap();
        console.log('✓ Carte initialisée');
        
        // Charger les établissements
        console.log('2. Chargement des établissements...');
        map.updateMapAndMarkers();
        console.log('✓ Établissements chargés');
        
        // Configurer les boutons de filtre
        console.log('3. Configuration des boutons de filtre...');
        filters.setupFilterButtons();
        console.log('✓ Boutons de filtre configurés');
        
        // Vérifier l'état initial
        console.log('4. Vérification de l\'état initial...');
        const initialFilters = filters.getActiveFilters();
        console.log('Filtres initiaux:', initialFilters);
        
        if (initialFilters.visited || initialFilters.unvisited || initialFilters.label) {
            throw new Error('Les filtres ne devraient pas être actifs initialement');
        }
        console.log('✓ État initial correct');
        
        // Tester le filtre "Visité"
        console.log('5. Test du filtre "Visité"...');
        const visitedButton = document.getElementById('filter-visited');
        if (!visitedButton) {
            throw new Error('Bouton "Visité" introuvable');
        }
        
        // Simuler un clic sur le bouton
        visitedButton.click();
        
        // Attendre un court instant pour que les changements soient appliqués
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const afterVisitedFilter = filters.getActiveFilters();
        console.log('Filtres après clic sur "Visité":', afterVisitedFilter);
        
        if (!afterVisitedFilter.visited) {
            throw new Error('Le filtre "Visité" devrait être actif');
        }
        console.log('✓ Filtre "Visité" fonctionne');
        
        // Tester le filtre "Tous"
        console.log('6. Test du filtre "Tous"...');
        const allButton = document.getElementById('filter-all');
        if (!allButton) {
            throw new Error('Bouton "Tous" introuvable');
        }
        
        allButton.click();
        
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const afterAllFilter = filters.getActiveFilters();
        console.log('Filtres après clic sur "Tous":', afterAllFilter);
        
        if (afterAllFilter.visited || afterAllFilter.unvisited || afterAllFilter.label) {
            throw new Error('Aucun filtre ne devrait être actif après "Tous"');
        }
        console.log('✓ Filtre "Tous" fonctionne');
        
        console.log('\n✅ Tous les tests ont passé !');
        console.log('Les filtres fonctionnent correctement après la refactorisation.');
        
    } catch (error) {
        console.error('❌ Test échoué:', error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

// Exécuter le test
runTest();

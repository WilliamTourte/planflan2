/**
 * Test pour vérifier que la carte n'est pas initialisée deux fois
 * Ce test simule le chargement de la page liste_etablissements.html
 */

// Simuler les éléments DOM nécessaires
const mockMapElement = document.createElement('div');
mockMapElement.id = 'map';
document.body.appendChild(mockMapElement);

const mockEtablissementsData = document.createElement('div');
mockEtablissementsData.id = 'etablissements-data';
mockEtablissementsData.setAttribute('data-etablissements', JSON.stringify([
    {
        id_etab: 1,
        nom: "Test Etablissement",
        adresse: "123 Rue Test",
        ville: "TestVille",
        latitude: 48.8566,
        longitude: 2.3522,
        visite: false,
        label: false,
        flans: []
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

// Charger les modules
import * as map from './app/static/js/map.js';

console.log('Test: Initialisation de la carte une seule fois...');

// Première initialisation (simule map_filter.js)
try {
    console.log('Première initialisation...');
    map.initMap();
    console.log('✓ Première initialisation réussie');
} catch (error) {
    console.error('✗ Erreur lors de la première initialisation:', error.message);
    process.exit(1);
}

// Deuxième initialisation (simule main.js)
try {
    console.log('Deuxième initialisation...');
    map.initMap();
    console.error('✗ ERREUR: La carte a été initialisée deux fois sans erreur !');
    console.error('Cela indique que le problème de double initialisation n\'est pas corrigé.');
    process.exit(1);
} catch (error) {
    if (error.message.includes('Map container is already initialized')) {
        console.log('✓ Deuxième initialisation a échoué comme prévu:', error.message);
        console.log('✓ Le problème de double initialisation est corrigé !');
    } else {
        console.error('✗ Erreur inattendue lors de la deuxième initialisation:', error.message);
        process.exit(1);
    }
}

console.log('\nTest terminé avec succès !');
console.log('La carte ne peut être initialisée qu\'une seule fois, ce qui prévient l\'erreur originale.');

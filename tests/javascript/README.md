# Tests JavaScript pour PlanFlan

Ce dossier contient les tests pour le code JavaScript de l'application PlanFlan.

## Structure

```
tests/javascript/
├── __mocks__/          # Mocks pour les requêtes API et autres dépendances
├── unit/              # Tests unitaires pour les modules individuels
├── integration/       # Tests d'intégration pour les interactions entre modules
├── setupTests.js      # Configuration globale pour Jest
└── README.md          # Ce fichier
```

## Prérequis

- Node.js (version 14 ou supérieure)
- npm (version 6 ou supérieure)

## Installation

1. Installer les dépendances :

```bash
npm install
```

## Exécution des tests

### Tous les tests

```bash
npm test
```

### Tests unitaires uniquement

```bash
npm run test:unit
```

### Tests d'intégration uniquement

```bash
npm run test:integration
```

### Mode watch (développement)

```bash
npm run test:watch
```

## Configuration

Les tests utilisent les outils suivants :

- **Jest** : Framework de test
- **jsdom** : Environnement DOM pour les tests
- **fetch-mock** : Mock des requêtes HTTP
- **MSW (Mock Service Worker)** : Mock des API
- **Babel** : Transpilation du code ES6

## Écriture de nouveaux tests

### Tests unitaires

Les tests unitaires doivent :

1. Tester une fonction/méthode spécifique
2. Être isolés (utiliser des mocks)
3. Être rapides à exécuter
4. Couvrir les cas nominaux et les cas d'erreur

Exemple :

```javascript
describe('maFonction', () => {
  it('should do something', () => {
    // Setup
    const result = maFonction(arg1, arg2);
    
    // Assertion
    expect(result).toBe(expected);
  });

  it('should handle errors', () => {
    // Setup avec mock d'erreur
    const mockFn = jest.fn().mockRejectedValue(new Error('test'));
    
    // Assertion d'erreur
    await expect(maFonction(mockFn)).rejects.toThrow('test');
  });
});
```

### Tests d'intégration

Les tests d'intégration doivent :

1. Tester l'interaction entre plusieurs modules
2. Utiliser un DOM simulé (jsdom)
3. Vérifier les flux complets
4. Être plus réalistes que les tests unitaires

Exemple :

```javascript
describe('Feature: Autocomplete et API', () => {
  beforeEach(() => {
    // Configurer le DOM
    document.body.innerHTML = `
      <input id="ville-autocomplete">
      <div id="autocomplete-results"></div>
    `;
  });

  it('should show results when typing', async () => {
    // Mock de l'API
    fetchMock.get('/api/villes?q=Par', ['Paris', 'Paris 1er']);
    
    // Initialiser le module
    initAutocomplete();
    
    // Simuler la saisie utilisateur
    const input = document.getElementById('ville-autocomplete');
    input.value = 'Par';
    input.dispatchEvent(new Event('input'));
    
    // Attendre et vérifier
    await new Promise(resolve => setTimeout(resolve, 100));
    expect(document.getElementById('autocomplete-results').children.length).toBe(2);
  });
});
```

## Bonnes pratiques

1. **Noms de tests clairs** : Utiliser `should` pour décrire le comportement attendu
2. **Isolation** : Nettoyer les mocks et le DOM après chaque test
3. **Performance** : Éviter les attentes inutiles (`setTimeout`)
4. **Coverage** : Viser 80%+ de couverture de code
5. **Maintenabilité** : Garder les tests simples et lisibles

## Intégration CI/CD

Les tests JavaScript sont automatiquement exécutés dans le pipeline CI/CD via GitHub Actions. Voir `.github/workflows/ci.yml` pour la configuration.

## Dépannage

### Erreur : "Cannot find module"

```bash
npm install
```

### Erreur : "Jest not found"

```bash
npm install --save-dev jest
```

### Problèmes de cache

```bash
npm cache clean --force
rm -rf node_modules/
npm install
```

## Ressources

- [Documentation Jest](https://jestjs.io/)
- [Documentation jsdom](https://github.com/jsdom/jsdom)
- [Documentation fetch-mock](https://www.wheresrhys.co.uk/fetch-mock/)
- [Documentation MSW](https://mswjs.io/)
# Optimisations Lighthouse pour index.html

## Contexte

Suite à l'analyse Lighthouse du 13/01/2026, plusieurs opportunités d'optimisation ont été identifiées pour améliorer les performances de la page d'accueil. Ce document détaille les 4 optimisations prioritaires à implémenter.

## 1. Ajout de font-display: swap

### Problème identifié
- Les polices Bubblegum.ttf et bootstrap-icons.woff2 bloquent le rendu du texte pendant 580ms
- Impact sur le FCP (First Contentful Paint) et l'expérience utilisateur
- Texte invisible pendant le chargement des polices

### Solution technique

**Fichier à modifier** : `app/static/css/style.css`

```css
/* Ajouter dans la déclaration @font-face existante */
@font-face {
  font-family: 'Bubblegum';
  src: url('/static/fonts/Bubblegum.ttf');
  font-display: swap; /* Nouvelle propriété */
}

/* Pour les icônes Bootstrap (si utilisé localement) */
@font-face {
  font-family: 'bootstrap-icons';
  src: url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.woff2');
  font-display: swap;
}
```

### Impact estimé
- **Réduction FCP** : 580ms
- **Expérience utilisateur** : Texte visible immédiatement avec police de fallback
- **Score Lighthouse** : +15-20 points sur Performance

### Validation
- Vérifier dans Chrome DevTools > Application > Fonts que `font-display: swap` est appliqué
- Tester le rendu avec connexion lente (throttling 3G)

## 2. Inlining du CSS critique

### Problème identifié
- style.css (33.2 KiB) bloque le rendu initial pendant 900ms
- Chemin critique trop long avec dépendance CSS externe
- 402ms de latence réseau pour le fichier CSS

### Solution technique

**Fichier à modifier** : `app/templates/base.html`

```html
<!-- Dans la section <head>, avant le CSS externe -->
<style>
  /* CSS critique pour le rendu above-the-fold */
  body {
    margin: 0;
    font-family: sans-serif;
    background: #f8f9fa;
    line-height: 1.6;
  }
  
  .header {
    background: #fff;
    box-shadow: 0 2px 4px rgba(0,0,0,.1);
    position: relative;
    z-index: 1000;
  }
  
  .main-container {
    min-height: 80vh;
    padding: 20px 0;
  }
  
  .btn, .btn-primary {
    display: inline-block;
    padding: 8px 16px;
    background: #0d6efd;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  /* Layout de base pour éviter les reflows */
  .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
  }
  
  /* Styles pour le contenu visible immédiatement */
  h1, h2, h3 {
    font-weight: 600;
    margin: 0 0 15px;
  }
  
  p {
    margin: 0 0 15px;
  }
</style>

<!-- Chargement asynchrone du CSS complet -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}" media="print" onload="this.media='all'">
<noscript>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</noscript>
```

### Impact estimé
- **Réduction chemin critique** : 900ms
- **LCP amélioré** : Rendu initial 30-50% plus rapide
- **Score Lighthouse** : +20-30 points sur Performance

### Validation
- Vérifier dans Chrome DevTools > Network que le CSS est chargé avec `media="print"` initialement
- Confirmer que le rendu de base est fonctionnel sans le CSS complet

## 3. Déferrement des scripts JavaScript

### Problème identifié
- 10 fichiers JS bloquants dans le chemin critique
- Total de 120 KiB de JavaScript bloquant le rendu
- Impact majeur sur LCP et interactivité

### Solution technique

**Fichier à modifier** : `app/templates/base.html`

```html
<!-- Scripts critiques (nécessaires pour le rendu initial) -->
<!-- Ces scripts doivent rester sans defer si ils sont nécessaires pour le contenu above-the-fold -->
<script src="{{ url_for('static', filename='js/base.js') }}"></script>

<!-- Scripts non-critiques (à déférer) -->
<script src="{{ url_for('static', filename='js/dashboard.js') }}" defer></script>
<script src="{{ url_for('static', filename='js/filters.js') }}" defer></script>
<script src="{{ url_for('static', filename='js/map.js') }}" defer></script>
<script src="{{ url_for('static', filename='js/autocomplete.js') }}" defer></script>
<script src="{{ url_for('static', filename='js/api.js') }}" defer></script>
<script src="{{ url_for('static', filename='js/utils.js') }}" defer></script>
<script src="{{ url_for('static', filename='js/macros.js') }}" defer></script>
<script src="{{ url_for('static', filename='js/geolocation.js') }}" defer></script>
<script src="{{ url_for('static', filename='js/index.js') }}" defer></script>

<!-- Pour les scripts qui doivent s'exécuter dans un ordre spécifique -->
<script>
  // Si nécessaire, gérer les dépendances entre scripts
  document.addEventListener('DOMContentLoaded', function() {
    // Initialisation qui dépend de plusieurs scripts
  });
</script>
```

### Impact estimé
- **Réduction rendu initial** : 1,070ms
- **Parallélisation** : Chargement simultané des scripts
- **Score Lighthouse** : +25-35 points sur Performance

### Validation
- Vérifier dans Chrome DevTools > Network que les scripts ont bien l'attribut `defer`
- Tester que toutes les fonctionnalités restent opérationnelles
- Confirmer que l'ordre d'exécution est respecté si nécessaire

## 4. Préconnexion aux origines critiques

### Problème identifié
- Aucune préconnexion aux CDN externes
- Établissement de connexion tardif pour les ressources critiques
- Impact sur toutes les requêtes vers jsdelivr.net

### Solution technique

**Fichier à modifier** : `app/templates/base.html`

```html
<!-- Dans la section <head>, aussi haut que possible -->

<!-- Préconnexions aux CDN externes -->
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="dns-prefetch" href="https://cdn.jsdelivr.net">

<!-- Préconnexion aux ressources locales critiques -->
<link rel="preconnect" href="{{ url_for('static', filename='fonts/Bubblegum.ttf') }}" crossorigin>

<!-- Préchargement des ressources critiques -->
<link rel="preload" href="{{ url_for('static', filename='fonts/Bubblegum.ttf') }}" as="font" type="font/ttf" crossorigin>

<!-- Pour les ressources CDN critiques -->
<link rel="preload" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" as="style" crossorigin>
<link rel="preload" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.woff2" as="font" type="font/woff2" crossorigin>
```

### Impact estimé
- **Réduction latence CDN** : 100-300ms
- **Connexions plus rapides** : Établissement précoce des connexions
- **Score Lighthouse** : +10-15 points sur Performance

### Validation
- Vérifier dans Chrome DevTools > Network que les connexions sont établies tôt
- Confirmer que les ressources préchargées sont utilisées
- Tester avec throttling réseau pour voir l'impact

## Stratégie d'implémentation

### Ordre recommandé
1. **font-display: swap** (impact immédiat, risque minimal)
2. **Préconnexions** (simple à implémenter)
3. **Inlining CSS** (test nécessaire)
4. **Defer JS** (validation fonctionnelle requise)

### Tests recommandés
- **Fonctionnel** : Vérifier que toutes les features fonctionnent
- **Visuel** : Confirmer l'absence de régression d'affichage
- **Performance** : Mesurer avec Lighthouse avant/après chaque changement

### Outils de validation
- Chrome DevTools (Network, Performance, Application tabs)
- WebPageTest (test multi-étapes)
- Lighthouse CI (intégration dans le pipeline)

## Impact global estimé

| Optimisation | Réduction temps | Gain Lighthouse |
|--------------|-----------------|------------------|
| font-display  | 580ms           | +15-20 points   |
| CSS inlining  | 900ms           | +20-30 points   |
| JS defer      | 1,070ms         | +25-35 points   |
| Préconnexions | 100-300ms       | +10-15 points   |
| **Total**     | **2,550-2,850ms** | **+70-100 points** |

## Prochaines étapes après ces optimisations

1. **Configurer HTTP/2** sur le serveur Nginx
2. **Implémenter un cache agressif** pour les ressources statiques
3. **Optimiser les images** (WebP, lazy loading, compression)
4. **Minifier et combiner** les ressources JS/CSS
5. **Implémenter un Service Worker** pour le caching offline

## Références

- [MDN font-display](https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display)
- [Google Web Fundamentals - Critical CSS](https://developers.google.com/web/fundamentals/performance/critical-rendering-path/optimize-css-delivery)
- [Defer vs Async](https://flaviocopes.com/javascript-async-defer/)
- [Resource Hints](https://w3c.github.io/resource-hints/)

---

*Document généré le 13/01/2026 - Basé sur l'analyse Lighthouse de planflan.fr*
*Version: 1.0*
```
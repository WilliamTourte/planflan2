# Guide de Style CSS - PlanFlan

## 📁 Structure des Fichiers

```
app/static/css/
├── style.css          # Fichier principal (généré/optimisé)
├── components/        # Composants individuels (optionnel)
│   ├── header.css
│   ├── cards.css
│   └── ...
└── utilities/         # Classes utilitaires (optionnel)
    ├── spacing.css
    └── colors.css
```

## 🎨 Conventions de Nommage

### 1. Méthodologie BEM (recommandée)
```css
/* Block - Composant autonome */
.carte { ... }

/* Element - Partie d'un block */
.carte__header { ... }
.carte__image { ... }

/* Modifier - Variante d'un block */
.carte--featured { ... }
.carte--small { ... }
```

### 2. Préfixes pour les composants
- `.btn-*` - Boutons
- `.carte-*` - Cartes
- `.form-*` - Formulaires
- `.header-*` - Header
- `.footer-*` - Footer

### 3. Classes utilitaires
```css
.text-center { text-align: center; }
.mt-1 { margin-top: 4px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 15px; }
.p-1 { padding: 4px; }
.p-2 { padding: 8px; }
.p-3 { padding: 15px; }
```

## 📏 Structure d'un Composant

```css
/* =============================================
   COMPONENT-NAME - Description
   ============================================= */

.component-name {
  /* Styles de base */
}

.component-name__element {
  /* Styles des éléments */
}

.component-name--modifier {
  /* Styles des variantes */
}

@media (min-width: 768px) {
  /* Styles responsive */
}
```

## 🎨 Couleurs et Variables

### Variables CSS (dans `:root`)
```css
:root {
  --color-primary: #ffcf40;
  --color-secondary: #799dcb;
  --color-danger: #ff0000;
  --color-text: #000000;
  --color-text-light: #7f8c8d;
  --border-radius: 10px;
  --box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
```

### Utilisation
```css
.button {
  background-color: #ffcf40; /* Fallback */
  background-color: var(--color-primary); /* Variable */
}
```

## 📱 Approche Mobile-First

```css
/* Base styles (mobile) */
.component {
  width: 100%;
}

/* Tablet and up */
@media (min-width: 768px) {
  .component {
    width: 50%;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .component {
    width: 33.33%;
  }
}
```

## ⚠️ Règles à Éviter

### ❌ À ne pas faire
```css
/* Sélecteurs d'ID - À éviter */
#header { ... }

/* !important - À éviter */
.color { color: red !important; }

/* Sélecteurs trop spécifiques */
body div.container .header .nav ul li a { ... }

/* Duplication de code */
.button { color: red; }
.btn { color: red; }
```

### ✅ À faire à la place
```css
/* Utiliser des classes */
.header { ... }

/* Meilleure spécificité */
.button.primary { ... }

/* Variables et mixins */
:root { --color-red: #ff0000; }
.button { color: var(--color-red); }
```

## 🔧 Outils et Workflow

### Stylelint
- Configuration: `.stylelintrc.cjs`
- Commandes:
  ```bash
  npm run lint:css        # Vérifier
  npm run lint:css --fix  # Corriger automatiquement
  ```

### Prettier
- Configuration: `.prettierrc`
- Commandes:
  ```bash
  npm run format        # Formater tous les fichiers
  npm run format:check  # Vérifier la mise en forme
  ```

### Git Hooks
- Pre-commit hook avec Husky et lint-staged
- Vérifie automatiquement:
  - CSS avec Stylelint
  - JavaScript avec ESLint
  - Formatage avec Prettier

## 📝 Bonnes Pratiques

### 1. Organisation
- Un composant = Un fichier (si projet complexe)
- Regrouper les media queries par composant
- Commentaires clairs et concis

### 2. Performance
- Éviter `@import` (préférer plusieurs `<link>`)
- Minifier le CSS en production
- Utiliser `will-change` pour les animations

### 3. Accessibilité
- Couleurs contrastées (WCAG)
- `prefers-reduced-motion` pour les animations
- Taille de police relative (rem/em)

### 4. Maintenabilité
- Documentation des composants complexes
- Variables pour les valeurs répétées
- Nommage explicite

## 🚀 Déploiement

### En développement
```bash
# Vérifier tout avant commit
npm run lint:css
npm run format
```

### En production
```bash
# Minification et optimisation
# (à configurer selon votre pipeline)
```

## 📚 Ressources

- [CSS Guidelines](https://cssguidelin.es/)
- [BEM Methodology](http://getbem.com/)
- [Stylelint Documentation](https://stylelint.io/)
- [Prettier Documentation](https://prettier.io/)

---

*Dernière mise à jour: 30/01/2026*
*Mainteneur: [Votre Nom]*

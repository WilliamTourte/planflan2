# Solution pour centrer le popup Leaflet

## Problème identifié
Le popup Leaflet ne s'affiche pas correctement et n'est pas centré sur la carte. Le fichier CSS a été corrompu par des modifications successives, ce qui a créé des conflits et des doublons.

## Solution recommandée

### Étape 1 : Restaurer le fichier CSS original
```bash
cd C:\Users\dhugonnard2025\PycharmProjects\PythonProject\planflan3
git checkout HEAD -- app\static\css\style.css
```

### Étape 2 : Appliquer la correction CSS minimale
Remplacer la section Leaflet (autour de la ligne 659) par cette version propre et fonctionnelle :

```css
/* =============================================
   15. LEAFLET - INFOWINDOWS & EMOJIS
   ============================================= */
.leaflet-popup-content-wrapper {
    width: var(--infowindow-width);
    max-width: var(--infowindow-max-width);
    font-size: var(--font-size-md);
    margin: 0 !important;
    z-index: 999999 !important;
}

.leaflet-popup-content {
    width: var(--infowindow-width);
    margin: 0 auto;
    padding: var(--padding-md);
    background: white;
    text-align: center;
}

.leaflet-popup-close-button {
    font-size: 18px;
    top: 5px;
    right: 5px;
}

.leaflet-popup-tip {
    left: 50% !important;
    margin-left: -10px !important;
}
```

### Étape 3 : Vérifier le JavaScript
S'assurer que dans `map_filter.js`, les popups sont créés avec ces options :

```javascript
const popup = L.popup({
    autoPan: true,
    autoPanPadding: [50, 50], // Marge pour éviter que le popup soit collé aux bords
    keepInView: true,
    closeButton: true,
    className: 'custom-popup',
    maxWidth: 250
});
```

### Étape 4 : Tester la solution
1. Vérifier que le popup s'affiche correctement
2. Vérifier que le contenu est centré visuellement
3. Tester dans différents navigateurs
4. Vérifier que le z-index est suffisant pour que le popup apparaisse au-dessus de tous les éléments

## Explications techniques

### Pourquoi cette solution fonctionne :
1. **Respect du fonctionnement natif de Leaflet** : On ne force pas le positionnement manuel, on laisse Leaflet gérer cela
2. **Centrage visuel propre** : `margin: 0 auto` centre le contenu horizontalement
3. **z-index élevé** : 999999 garantit que le popup apparaît au-dessus de tous les autres éléments
4. **Pointe du popup centrée** : La flèche du popup est correctement positionnée

### Ce qui a été supprimé :
- Toutes les tentatives de positionnement manuel (`left`, `transform`, etc.) qui interféraient avec Leaflet
- Les doublons et conflits CSS
- Les règles inutiles qui n'affectaient pas le centrage

### Ce qui a été conservé :
- Les styles de base (largeur, padding, couleurs)
- Le z-index élevé pour la visibilité
- Le centrage visuel du contenu
- La pointe du popup centrée

## Solution alternative si problème persiste

Si le popup ne s'affiche toujours pas correctement, essayer cette approche plus directe :

```css
/* Solution alternative - forcer le positionnement absolu */
.leaflet-popup {
    position: absolute !important;
    z-index: 999999 !important;
}

.leaflet-popup-content-wrapper {
    position: relative !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: var(--infowindow-width);
    max-width: var(--infowindow-max-width);
    margin: 0 !important;
    z-index: 999999 !important;
}
```

## Vérification finale

Après application de la solution :
- Le popup devrait s'afficher correctement
- Le contenu devrait être centré visuellement
- La pointe du popup devrait être centrée sous le popup
- Le popup devrait apparaître au-dessus de tous les autres éléments de la carte

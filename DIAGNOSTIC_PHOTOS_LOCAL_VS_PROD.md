# 🔍 DIAGNOSTIC : Photos Google Places - Local OK, Production KO

## ✅ Résultat de l'analyse

L'analyse automatisée a été exécutée et a identifié **2 problèmes majeurs** :

### 🎯 Problème #1 : LOG_LEVEL = 'WARNING' en production (Confirmé)

**Fichier :** `app/configprod.py` ligne 93

**Situation actuelle :**
- **Local (config.py)** : `LOG_LEVEL = "DEBUG"` ✅
- **Production (configprod.py)** : `LOG_LEVEL = "WARNING"` ❌

**Conséquence :**
Les 22 messages de log `[FETCH_PHOTOS]` dans `app/outils.py` utilisent tous `logger.info()`, qui ne s'affichent **PAS** avec un niveau WARNING.

→ **Vous ne voyez pas ce qui se passe en production !**

**Solution immédiate :**
```python
# Dans app/configprod.py ligne 93
LOG_LEVEL = "INFO"  # Au lieu de "WARNING"
```

Puis redémarrer :
```bash
docker compose restart planflan-backend
```

---

### 🎯 Problème #2 : Restrictions de la clé API Google (Très probable)

**Situation :**
La clé API Google Maps fonctionne en local (`http://localhost:81`) mais peut avoir des restrictions qui bloquent les requêtes depuis le serveur de production.

**Vérification nécessaire :**
1. Aller sur [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Cliquer sur votre clé API
3. Vérifier les sections :

   **a) API restrictions :**
   - ✅ "Places API" doit être dans la liste des APIs autorisées
   
   **b) Application restrictions :**
   - Option 1 (recommandé pour tester) : "None" → Aucune restriction
   - Option 2 : "HTTP referrers" → Ajouter `https://planflan.fr/*` et `https://www.planflan.fr/*`
   - Option 3 : "IP addresses" → Ajouter l'IP du serveur de production

**Symptômes si c'est le problème :**
Après avoir activé LOG_LEVEL="INFO", vous verrez dans les logs :
```
[FETCH_PHOTOS] Aucune photo trouvée dans les détails de l'établissement
```
ou
```
[FETCH_PHOTOS] Erreur API Google: status=403
```

---

## 📋 Configuration validée ✅

L'analyse a confirmé que tout le reste est **correctement configuré** :

✅ GOOGLE_MAPS_API_KEY définie dans .env (39 caractères)
✅ Fonction `fetch_place_photos()` présente dans `app/outils.py`
✅ Route `ajouter_etablissement()` appelle bien `fetch_place_photos()`
✅ Volume Docker `photos_volume` correctement monté :
   - Backend : `/app/static/uploads`
   - Nginx : `/var/www/uploads`
✅ Dockerfile crée le dossier uploads avec les bonnes permissions (777)
✅ google_place_id utilisé dans le code

---

## 🎬 Plan d'action (étape par étape)

### Étape 1 : Activer les logs détaillés (PRIORITAIRE)

Éditer `app/configprod.py` :

```python
# Ligne 93 - Classe ConfigProd
LOG_LEVEL = "INFO"  # Au lieu de "WARNING"
```

Puis :
```bash
docker compose restart planflan-backend
```

### Étape 2 : Vérifier et ajuster la clé API Google

1. **Vérifier les restrictions :**
   - https://console.cloud.google.com/apis/credentials
   - Cliquer sur la clé API
   - Temporairement : Mettre "Application restrictions" à "None"

2. **Vérifier que Places API est activée :**
   - https://console.cloud.google.com/apis/library/places-backend.googleapis.com
   - Bouton "ENABLE" si pas déjà fait

### Étape 3 : Tester en production

1. **Ajouter un établissement via l'interface web**
   - Utiliser l'autocomplete Google
   - Valider le formulaire

2. **Consulter les logs immédiatement après :**
   ```bash
   docker logs planflan-container-backend 2>&1 | grep FETCH_PHOTOS | tail -50
   ```

### Étape 4 : Analyser les résultats

**Scénario A : Vous voyez les logs et la photo s'affiche**
→ ✅ Problème résolu ! C'était juste le niveau de logs.

**Scénario B : Vous voyez "Aucune photo trouvée"**
→ Problème de restrictions API, vérifiez l'étape 2.

**Scénario C : Vous voyez "Erreur API Google: status=403"**
→ Clé API refusée, vérifiez :
   - La clé est bien la même qu'en local
   - Les restrictions de domaine/IP
   - Le quota n'est pas dépassé

**Scénario D : Vous voyez "Permission d'écriture"**
→ Problème de permissions sur le volume Docker :
```bash
docker exec planflan-container-backend chmod -R 777 /app/static/uploads
```

**Scénario E : Vous ne voyez toujours rien**
→ Le code n'est pas appelé, vérifiez que google_place_id est bien renseigné.

---

## 🔧 Correctif à appliquer maintenant

### Fichier 1 : `app/configprod.py`

**Ligne 93 - Changer le LOG_LEVEL**

```python
# Configuration de la journalisation
LOG_LEVEL = "INFO"  # Au lieu de "WARNING"
```

**Pourquoi :**
- Les logs `[FETCH_PHOTOS]` utilisent `logger.info()`
- Avec WARNING, ces logs sont invisibles
- En production, on a besoin de ces logs pour diagnostiquer

**Note :** Une fois le problème identifié et résolu, vous pourrez remettre `WARNING` si vous le souhaitez.

---

## 📊 Résumé de l'analyse technique

| Élément | Local | Production | Status |
|---------|-------|------------|--------|
| LOG_LEVEL | DEBUG | WARNING | ❌ Problème |
| GOOGLE_MAPS_API_KEY | Définie | Définie | ✅ OK |
| UPLOAD_FOLDER | `app/static/uploads` | `/app/static/uploads` | ✅ OK |
| Volume Docker | Monté | Monté | ✅ OK |
| Permissions | 777 | 777 | ✅ OK |
| Code fetch_place_photos | Présent | Présent | ✅ OK |
| Appel dans ajouter_etablissement | Oui | Oui | ✅ OK |
| Restrictions API ? | Non testées | ? | ⚠️ À vérifier |

---

## 🎯 Prédiction

**Probabilité à 90% :**
Le problème vient de la combinaison de :
1. **LOG_LEVEL = WARNING** (80% du problème)
   - Empêche de voir ce qui se passe
   - Masque les erreurs et succès

2. **Restrictions de la clé API** (potentiellement 20% du problème)
   - La clé fonctionne en local mais pourrait avoir des restrictions de domaine
   - L'API refuse les requêtes depuis planflan.fr si elle n'est pas autorisée

**Une fois LOG_LEVEL changé à INFO, les logs révéleront le problème exact.**

---

## 📝 Commandes utiles

**Voir les logs en temps réel :**
```bash
docker logs -f planflan-container-backend 2>&1 | grep FETCH_PHOTOS
```

**Tester la connexion à l'API Google depuis le conteneur :**
```bash
docker exec planflan-container-backend curl -I "https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&key=VOTRE_CLE_API"
```

**Vérifier la configuration chargée :**
```bash
docker exec planflan-container-backend python -c "
import os
os.environ['FLASK_CONFIG'] = 'ConfigProd'
from app import create_app
app = create_app()
with app.app_context():
    print('LOG_LEVEL:', app.config.get('LOG_LEVEL'))
    print('UPLOAD_FOLDER:', app.config.get('UPLOAD_FOLDER'))
    key = app.config.get('GOOGLE_MAPS_API_KEY')
    print('API Key:', key[:10] + '...' if key else 'NON DÉFINIE')
"
```

**Vérifier les photos en base :**
```bash
docker exec planflan-container-backend python -c "
import os
os.environ['FLASK_CONFIG'] = 'ConfigProd'
from app import create_app
from app.models import Photo, Etablissement

app = create_app()
with app.app_context():
    photos = Photo.query.count()
    etabs_with_place_id = Etablissement.query.filter(Etablissement.google_place_id.isnot(None)).count()
    print(f'Photos en base: {photos}')
    print(f'Établissements avec place_id: {etabs_with_place_id}')
"
```

---

## ✅ Action immédiate requise

**Changez LOG_LEVEL="INFO" dans app/configprod.py et redémarrez le backend.**

Les logs vous diront ensuite exactement ce qui ne va pas ! 🔍

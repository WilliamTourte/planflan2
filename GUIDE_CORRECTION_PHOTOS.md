# 🚀 GUIDE RAPIDE : Correction du problème de photos en production

## ✅ Ce qui a été fait

1. **Analyse complète du problème** ✓
2. **Identification de la cause principale** ✓
3. **Application du correctif** ✓

## 📝 Résumé du problème

**Symptôme :** Les photos Google Places s'affichent en local mais pas en production.

**Cause identifiée :** 
- `LOG_LEVEL = "WARNING"` dans `app/configprod.py` (ligne 91)
- Les logs `[FETCH_PHOTOS]` utilisent `logger.info()` qui ne s'affiche pas avec WARNING
- **Résultat :** Impossible de voir ce qui se passe en production

**Cause probable secondaire :**
- Restrictions de la clé API Google Maps (à vérifier après avoir activé les logs)

## 🔧 Correctif appliqué

**Fichier modifié :** `app/configprod.py`

**Ligne 91 :** 
```python
# AVANT
LOG_LEVEL = "WARNING"

# APRÈS
LOG_LEVEL = "INFO"
```

## 🎯 Actions à effectuer maintenant

### 1️⃣ Redémarrer le conteneur backend

```bash
cd /home/damien/PycharmProjects/planflan2
docker compose restart planflan-backend
```

### 2️⃣ Vérifier que la configuration est chargée

```bash
docker exec planflan-container-backend python test_config_prod.py
```

**Ce script va :**
- ✓ Afficher le LOG_LEVEL (doit être "INFO")
- ✓ Vérifier UPLOAD_FOLDER et les permissions
- ✓ Afficher les statistiques des photos en base
- ✓ Tester la connexion à l'API Google Places

### 3️⃣ Tester l'ajout d'un établissement

1. **Aller sur le site** (https://planflan.fr ou http://localhost:81)
2. **Ajouter un établissement** via l'autocomplete Google
3. **Observer les logs en temps réel :**

```bash
# Dans un terminal séparé
docker logs -f planflan-container-backend 2>&1 | grep FETCH_PHOTOS
```

### 4️⃣ Analyser les logs

Après avoir ajouté un établissement, vous devriez voir :

**✅ Scénario de succès :**
```
[FETCH_PHOTOS] Début pour établissement X, place_id=ChIJ...
[FETCH_PHOTOS] Appel de get_place_details pour place_id=ChIJ...
[FETCH_PHOTOS] 1 photo(s) disponible(s) dans l'API Google
[FETCH_PHOTOS] UPLOAD_FOLDER configuré: /app/static/uploads
[FETCH_PHOTOS] ✓ Permission d'écriture OK sur /app/static/uploads
[FETCH_PHOTOS] Téléchargement photo 0, reference=...
[FETCH_PHOTOS] Réponse API: status_code=200
[FETCH_PHOTOS] ✓ Fichier créé avec succès, taille=XXXXX octets
[FETCH_PHOTOS] Terminé, 1 photo(s) sauvegardée(s)
```

**❌ Problème de clé API :**
```
[FETCH_PHOTOS] Aucune photo trouvée dans les détails de l'établissement
```
→ Voir la section "Vérifier la clé API Google" ci-dessous

**❌ Restrictions API :**
```
[FETCH_PHOTOS] Erreur API Google: status=403
```
→ Voir la section "Vérifier la clé API Google" ci-dessous

## 🔑 Vérifier la clé API Google (si problème persiste)

### Étape 1 : Accéder à Google Cloud Console

1. Aller sur https://console.cloud.google.com/apis/credentials
2. Cliquer sur votre clé API

### Étape 2 : Vérifier les API autorisées

**Section "API restrictions" :**
- ✓ Doit contenir "Places API" (ou "None" pour tout autoriser)

Si Places API n'est pas dans la liste :
1. Aller sur https://console.cloud.google.com/apis/library/places-backend.googleapis.com
2. Cliquer sur "ENABLE"

### Étape 3 : Vérifier les restrictions d'application

**Section "Application restrictions" :**

**Option 1 (recommandée pour tester) :**
- Sélectionner "None"
- Sauvegarder

**Option 2 (pour sécuriser après) :**
- Sélectionner "HTTP referrers (web sites)"
- Ajouter :
  - `https://planflan.fr/*`
  - `https://www.planflan.fr/*`
  - `http://localhost:*/*` (pour le local)

**Option 3 :**
- Sélectionner "IP addresses (web servers, cron jobs, etc.)"
- Ajouter l'IP de votre serveur de production

### Étape 4 : Retester

Après avoir modifié les restrictions, attendez 2-3 minutes puis retestez l'ajout d'un établissement.

## 📊 Commandes de diagnostic utiles

### Voir tous les logs récents

```bash
docker logs planflan-container-backend 2>&1 | grep FETCH_PHOTOS | tail -50
```

### Voir les établissements avec photos

```bash
docker exec planflan-container-backend python -c "
import os
os.environ['FLASK_CONFIG'] = 'ConfigProd'
from app import create_app
from app.models import Etablissement, Photo

app = create_app()
with app.app_context():
    etabs = Etablissement.query.filter(Etablissement.google_place_id.isnot(None)).order_by(Etablissement.id_etab.desc()).limit(10).all()
    for etab in etabs:
        photos = Photo.query.filter_by(id_etab=etab.id_etab).count()
        print(f'[{etab.id_etab}] {etab.nom}: {photos} photo(s)')
"
```

### Vérifier les fichiers photos physiquement

```bash
docker exec planflan-container-backend ls -lh /app/static/uploads/ | head -20
```

### Tester l'API Google depuis le conteneur

```bash
docker exec planflan-container-backend curl -s \
  "https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&key=VOTRE_CLE_API" \
  | python -m json.tool
```

## 🎯 Résultat attendu

Après avoir appliqué ces corrections :

1. ✅ Les logs `[FETCH_PHOTOS]` apparaissent dans `docker logs`
2. ✅ Les photos sont téléchargées depuis Google Places
3. ✅ Les photos sont sauvegardées dans `/app/static/uploads`
4. ✅ Les photos sont enregistrées en base de données
5. ✅ Les photos s'affichent sur le site

## 📞 En cas de problème persistant

Si après ces étapes le problème persiste :

1. **Vérifier que la clé API fonctionne en local**
   - Si elle fonctionne en local, c'est bien un problème de restrictions
   
2. **Comparer les clés API**
   ```bash
   # Local
   grep GOOGLE_MAPS_API_KEY .env
   
   # Production (dans le conteneur)
   docker exec planflan-container-backend printenv GOOGLE_MAPS_API_KEY
   ```
   
3. **Vérifier le pare-feu**
   ```bash
   docker exec planflan-container-backend curl -I https://maps.googleapis.com/
   ```
   Si timeout → problème de pare-feu

4. **Consulter les documents créés :**
   - `DIAGNOSTIC_PHOTOS_LOCAL_VS_PROD.md` : Diagnostic complet
   - `ANALYSE_DIFFERENCES_LOCAL_PROD.md` : Analyse détaillée existante
   - Exécuter `python analyse_diff_photos.py` : Script d'analyse automatique

## 📝 Checklist finale

- [ ] `app/configprod.py` modifié (LOG_LEVEL = "INFO")
- [ ] Conteneur backend redémarré
- [ ] `test_config_prod.py` exécuté avec succès
- [ ] Ajout d'un établissement testé
- [ ] Logs `[FETCH_PHOTOS]` visibles
- [ ] Photos affichées sur le site

Si toutes les cases sont cochées → **Problème résolu !** ✅

---

**Dernière mise à jour :** Script d'analyse créé et exécuté avec succès
**Fichiers modifiés :** `app/configprod.py` (ligne 91)
**Prochaine étape :** Redémarrer le backend et tester

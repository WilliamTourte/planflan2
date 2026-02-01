# Script de récupération des photos Google Places

Ce dossier contient des scripts pour récupérer automatiquement les photos des établissements depuis l'API Google Places.

## Fichiers

- `fetch_all_place_photos.py` : Script Python principal qui parcourt tous les établissements et récupère leurs photos
- `fetch_all_place_photos.sh` : Script shell pour exécuter facilement le script Python depuis Docker

## Prérequis

1. Une clé API Google Places valide avec les permissions nécessaires
2. Docker et Docker Compose installés
3. Les conteneurs Docker de l'application PlanFlan en cours d'exécution

## Configuration

Assurez-vous que votre fichier `.env` contient les bonnes informations de connexion à la base de données.

## Utilisation depuis Docker

### Méthode 1: Exécuter directement depuis le conteneur

```bash
# Lancer les conteneurs (si ce n'est pas déjà fait)
docker-compose up -d

# Accéder au conteneur backend
docker exec -it planflan-container-backend bash

# Exécuter le script (remplacez VOTRE_CLE_API par votre clé API Google Places)
python /python-docker/scripts/fetch_all_place_photos.py VOTRE_CLE_API
```

### Méthode 2: Utiliser le script shell

```bash
# Lancer les conteneurs (si ce n'est pas déjà fait)
docker-compose up -d

# Exécuter le script shell directement
docker exec -it planflan-container-backend /python-docker/scripts/fetch_all_place_photos.sh VOTRE_CLE_API
```

### Méthode 3: Exécuter depuis l'extérieur du conteneur

```bash
# Exécuter le script Python directement depuis votre machine hôte
docker exec -it planflan-container-backend python -c "
from app.outils import fetch_place_photos;
from app.models import Etablissement;
from app import create_app, db;

api_key = 'VOTRE_CLE_API';
app = create_app(config_class='ConfigProd');

with app.app_context():
    etablissements = Etablissement.query.filter(
        Etablissement.statut == 'VALIDE',
        Etablissement.google_place_id.isnot(None)
    ).all();
    
    for etab in etablissements:
        print(f'Traitement de {etab.nom}...')
        fetch_place_photos(etab.id_etab, etab.google_place_id, api_key)
        print(f'Photos récupérées pour {etab.nom}')
"
```

## Fonctionnement du script

1. Le script récupère tous les établissements valides qui ont un `google_place_id`
2. Pour chaque établissement, il appelle la fonction `fetch_place_photos`
3. Les photos sont sauvegardées dans le dossier `static/uploads/`
4. Les informations sur les photos sont enregistrées dans la base de données
5. Le script affiche des statistiques à la fin de l'exécution

## Paramètres

- **GOOGLE_PLACES_API_KEY** : Votre clé API Google Places (obligatoire)
- **max_width** : Largeur maximale des photos (par défaut 400, modifiable dans le code)

## Notes importantes

1. Assurez-vous que votre clé API Google Places a les permissions nécessaires pour accéder à l'API Places et à l'API Photos
2. Le script ne récupère qu'une photo par établissement (limité dans le code)
3. Si des photos existent déjà pour un établissement, le script les conserve et ne les remplace pas
4. Le script ne traite que les établissements avec le statut "VALIDE"

## Dépannage

Si vous rencontrez des erreurs :

1. Vérifiez que votre clé API est valide
2. Assurez-vous que les conteneurs Docker sont en cours d'exécution
3. Vérifiez que la base de données est accessible
4. Consultez les logs du conteneur backend avec `docker logs planflan-container-backend`

## Exemple de sortie

```
Début de la récupération des photos pour tous les établissements...
Clé API utilisée: AIzaSyD...1234567890
Trouvé 5 établissements valides avec un google_place_id

Traitement de l'établissement 1: Boulangerie Martin
Google Place ID: ChIJN1t_tDeuEmsRUsoyG83frY4
✓ 1 photo(s) récupérée(s): ['/app/static/uploads/etab_1_photo_0.jpg']

Traitement de l'établissement 2: Pâtisserie Dupont
Google Place ID: ChIJN1t_tDeuEmsRUsoyG83frY5
✗ Aucun photo récupérée pour cet établissement

============================================================
STATISTIQUES FINALES
============================================================
Établissements traités: 5
Photos récupérées: 3
Établissements sans photos: 2
Erreurs rencontrées: 0

Script terminé avec succès !
```
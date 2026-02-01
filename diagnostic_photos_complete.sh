#!/bin/bash

# Script de diagnostic complet pour le problème des photos Google Places
# en production vs Docker local

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  DIAGNOSTIC COMPLET - PHOTOS GOOGLE PLACES                     ║${NC}"
echo -e "${BLUE}║  Local vs Production                                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Fonction pour afficher un titre de section
section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Fonction pour vérifier si on est en production ou en local
detect_environment() {
    if docker compose ps | grep -q "planflan-container-backend"; then
        echo "production"
    else
        echo "local"
    fi
}

ENV=$(detect_environment)

section "1. ENVIRONNEMENT DÉTECTÉ"
echo -e "Environnement: ${GREEN}$ENV${NC}"

section "2. VÉRIFICATION DES CONTENEURS"
docker compose ps

section "3. VÉRIFICATION DE LA CLÉ API GOOGLE MAPS"

# Vérifier dans le fichier .env
if [ -f .env ]; then
    GOOGLE_KEY=$(grep "GOOGLE_MAPS_API_KEY" .env | cut -d'=' -f2 | tr -d ' "')
    if [ -z "$GOOGLE_KEY" ]; then
        echo -e "${RED}✗ GOOGLE_MAPS_API_KEY non définie dans .env${NC}"
    else
        KEY_LENGTH=${#GOOGLE_KEY}
        echo -e "${GREEN}✓ GOOGLE_MAPS_API_KEY définie dans .env (longueur: $KEY_LENGTH caractères)${NC}"
        echo "   Préfixe: ${GOOGLE_KEY:0:10}..."
    fi
else
    echo -e "${RED}✗ Fichier .env introuvable${NC}"
fi

# Vérifier dans le conteneur
GOOGLE_KEY_CONTAINER=$(docker exec planflan-container-backend printenv GOOGLE_MAPS_API_KEY 2>/dev/null)
if [ -z "$GOOGLE_KEY_CONTAINER" ]; then
    echo -e "${RED}✗ GOOGLE_MAPS_API_KEY non chargée dans le conteneur${NC}"
else
    echo -e "${GREEN}✓ GOOGLE_MAPS_API_KEY chargée dans le conteneur${NC}"
    echo "   Préfixe: ${GOOGLE_KEY_CONTAINER:0:10}..."
fi

section "4. VÉRIFICATION DE LA CONFIGURATION FLASK"

docker exec planflan-container-backend python -c "
import os
import sys
os.environ['FLASK_CONFIG'] = 'ConfigProd'
from app import create_app
app = create_app()
with app.app_context():
    print('Configuration Flask:')
    print('  UPLOAD_FOLDER:', app.config.get('UPLOAD_FOLDER'))
    print('  Existe:', os.path.exists(app.config.get('UPLOAD_FOLDER', '')))
    print('  Écriture:', os.access(app.config.get('UPLOAD_FOLDER', ''), os.W_OK) if app.config.get('UPLOAD_FOLDER') else False)
    print('  LOG_LEVEL:', app.config.get('LOG_LEVEL'))

    key = app.config.get('GOOGLE_MAPS_API_KEY')
    if key:
        print(f'  GOOGLE_MAPS_API_KEY: {key[:10]}... (longueur: {len(key)})')
    else:
        print('  GOOGLE_MAPS_API_KEY: ✗ NON DÉFINIE')
" 2>&1

section "5. VÉRIFICATION DU DOSSIER UPLOADS (Backend)"

echo "Contenu de /app/static/uploads dans le backend:"
docker exec planflan-container-backend ls -lah /app/static/uploads/ 2>&1 | head -20

echo ""
echo "Test d'écriture:"
if docker exec planflan-container-backend touch /app/static/uploads/test_write.txt 2>/dev/null; then
    echo -e "${GREEN}✓ Écriture réussie${NC}"
    docker exec planflan-container-backend rm /app/static/uploads/test_write.txt 2>/dev/null
else
    echo -e "${RED}✗ Impossible d'écrire dans le dossier uploads${NC}"
fi

section "6. VÉRIFICATION DU VOLUME NGINX"

echo "Contenu de /var/www/uploads dans nginx:"
docker exec planflan-container-nginx ls -lah /var/www/uploads/ 2>&1 | head -20

section "7. VÉRIFICATION DE LA CONFIGURATION NGINX"

echo "Configuration du location /static/uploads/ dans nginx:"
docker exec planflan-container-nginx cat /etc/nginx/conf.d/default.conf 2>&1 | grep -A 5 "/static/uploads"

section "8. LOGS RÉCENTS - FETCH_PHOTOS"

echo "Derniers logs contenant [FETCH_PHOTOS]:"
docker logs planflan-container-backend 2>&1 | grep -i "FETCH_PHOTOS" | tail -30

if [ $(docker logs planflan-container-backend 2>&1 | grep -i "FETCH_PHOTOS" | wc -l) -eq 0 ]; then
    echo -e "${YELLOW}⚠ Aucun log [FETCH_PHOTOS] trouvé${NC}"
    echo "   Causes possibles:"
    echo "   1. Le code fetch_place_photos() n'a jamais été appelé"
    echo "   2. Le niveau de log est trop élevé (WARNING au lieu de INFO)"
    echo "   3. Les logs ont été purgés"
fi

section "9. LOGS RÉCENTS - ERREURS"

echo "Dernières erreurs dans les logs:"
docker logs planflan-container-backend 2>&1 | grep -i "error\|exception\|traceback" | tail -20

section "10. TEST DE CONNECTIVITÉ VERS GOOGLE PLACES API"

echo "Test de connexion vers l'API Google Places:"
docker exec planflan-container-backend curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" \
    "https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&key=${GOOGLE_KEY_CONTAINER}" 2>&1

section "11. VÉRIFICATION DE LA BASE DE DONNÉES"

echo "Établissements avec google_place_id dans la base:"
docker exec planflan-container-backend python -c "
import os
os.environ['FLASK_CONFIG'] = 'ConfigProd'
from app import create_app
from app.models import Etablissement, Photo

app = create_app()
with app.app_context():
    # Compter les établissements avec google_place_id
    etabs_with_place_id = Etablissement.query.filter(Etablissement.google_place_id.isnot(None)).count()
    etabs_without_place_id = Etablissement.query.filter(Etablissement.google_place_id.is_(None)).count()

    print(f'Établissements AVEC google_place_id: {etabs_with_place_id}')
    print(f'Établissements SANS google_place_id: {etabs_without_place_id}')

    # Photos en base
    photos_count = Photo.query.count()
    print(f'Photos en base de données: {photos_count}')

    # Derniers établissements ajoutés
    print('\nDerniers établissements ajoutés (avec place_id):')
    recent = Etablissement.query.filter(Etablissement.google_place_id.isnot(None)).order_by(Etablissement.id_etab.desc()).limit(5).all()
    for etab in recent:
        photos = Photo.query.filter_by(id_etab=etab.id_etab).count()
        print(f'  ID {etab.id_etab}: {etab.nom} - place_id: {etab.google_place_id[:20]}... - {photos} photo(s)')
" 2>&1

section "12. COMPARAISON CONFIG LOCAL vs PRODUCTION"

echo "Fichier de config chargé:"
docker exec planflan-container-backend python -c "
import os
print('FLASK_CONFIG:', os.environ.get('FLASK_CONFIG', 'NON DÉFINI'))
" 2>&1

section "13. RECOMMANDATIONS"

echo -e "${YELLOW}┌─────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${YELLOW}│ ACTIONS À VÉRIFIER / EFFECTUER                                  │${NC}"
echo -e "${YELLOW}└─────────────────────────────────────────────────────────────────┘${NC}"
echo ""
echo "1. Vérifier les restrictions de la clé API dans Google Cloud Console:"
echo "   → https://console.cloud.google.com/apis/credentials"
echo ""
echo "2. Si LOG_LEVEL = WARNING, le changer temporairement à INFO:"
echo "   → Éditer app/configprod.py"
echo "   → Changer LOG_LEVEL = 'INFO'"
echo "   → docker compose restart planflan-backend"
echo ""
echo "3. Tester manuellement l'ajout d'un établissement:"
echo "   → Aller sur le site"
echo "   → Ajouter un établissement avec autocomplete Google"
echo "   → Vérifier les logs immédiatement après"
echo ""
echo "4. Vérifier que docker-compose.yml monte bien le volume uploads:"
echo "   → cat docker-compose.yml | grep -A 5 uploads"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  DIAGNOSTIC TERMINÉ                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"

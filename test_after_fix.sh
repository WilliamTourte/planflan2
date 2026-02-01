#!/bin/bash

# Script de test rapide après correction
# Usage: ./test_after_fix.sh

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TEST APRÈS CORRECTION - Photos Google Places                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Vérifier que Docker est en cours d'exécution
echo -e "${YELLOW}[1/5]${NC} Vérification de Docker..."
if ! docker ps &> /dev/null; then
    echo -e "${RED}✗ Docker n'est pas en cours d'exécution${NC}"
    echo "  Démarrez Docker puis relancez ce script."
    exit 1
fi
echo -e "${GREEN}✓ Docker actif${NC}"
echo ""

# 2. Vérifier que les conteneurs sont démarrés
echo -e "${YELLOW}[2/5]${NC} Vérification des conteneurs..."
if ! docker ps | grep -q "planflan-container-backend"; then
    echo -e "${RED}✗ Conteneur backend non démarré${NC}"
    echo "  Lancez: docker compose up -d"
    exit 1
fi
echo -e "${GREEN}✓ Conteneur backend actif${NC}"
echo ""

# 3. Vérifier la configuration
echo -e "${YELLOW}[3/5]${NC} Test de la configuration..."
docker exec planflan-container-backend python test_config_prod.py
echo ""

# 4. Afficher les derniers logs FETCH_PHOTOS
echo -e "${YELLOW}[4/5]${NC} Derniers logs [FETCH_PHOTOS]..."
LOGS=$(docker logs planflan-container-backend 2>&1 | grep FETCH_PHOTOS | tail -10)
if [ -z "$LOGS" ]; then
    echo -e "${YELLOW}⚠ Aucun log [FETCH_PHOTOS] trouvé${NC}"
    echo "  Cela peut être normal si aucun établissement n'a été ajouté récemment."
    echo "  Testez l'ajout d'un établissement via l'interface web."
else
    echo "$LOGS"
fi
echo ""

# 5. Instructions pour la suite
echo -e "${YELLOW}[5/5]${NC} Instructions pour tester..."
echo ""
echo -e "${GREEN}Pour tester l'ajout d'un établissement :${NC}"
echo "  1. Ouvrez http://localhost:81 (ou https://planflan.fr en production)"
echo "  2. Dans un autre terminal, surveillez les logs :"
echo -e "     ${BLUE}docker logs -f planflan-container-backend 2>&1 | grep FETCH_PHOTOS${NC}"
echo "  3. Ajoutez un établissement avec l'autocomplete Google"
echo "  4. Vérifiez que les logs s'affichent et que la photo est téléchargée"
echo ""

echo -e "${GREEN}Pour voir les statistiques des photos :${NC}"
echo -e "  ${BLUE}docker exec planflan-container-backend python -c \"${NC}"
echo -e "  ${BLUE}import os${NC}"
echo -e "  ${BLUE}os.environ['FLASK_CONFIG'] = 'ConfigProd'${NC}"
echo -e "  ${BLUE}from app import create_app${NC}"
echo -e "  ${BLUE}from app.models import Photo, Etablissement${NC}"
echo -e "  ${BLUE}app = create_app()${NC}"
echo -e "  ${BLUE}with app.app_context():${NC}"
echo -e "  ${BLUE}    print('Photos:', Photo.query.count())${NC}"
echo -e "  ${BLUE}    print('Établissements avec place_id:', Etablissement.query.filter(Etablissement.google_place_id.isnot(None)).count())${NC}"
echo -e "  ${BLUE}\"${NC}"
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TEST TERMINÉ                                                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

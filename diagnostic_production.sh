#!/bin/bash
# Script de diagnostic pour serveur de PRODUCTION uniquement
# À exécuter sur le serveur distant où planflan.fr est hébergé

echo "=========================================="
echo "DIAGNOSTIC PHOTOS - PRODUCTION"
echo "=========================================="
echo ""
echo "Ce script doit être exécuté SUR LE SERVEUR DE PRODUCTION"
echo "où les conteneurs Docker de planflan.fr tournent."
echo ""

# Couleurs pour une meilleure lisibilité
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier que nous sommes bien sur le serveur de production
echo "1. Vérification de l'environnement"
echo "-----------------------------------"
if [ -f "docker-compose.override.yml" ]; then
    echo -e "${YELLOW}⚠️  ATTENTION : docker-compose.override.yml détecté${NC}"
    echo "   Ceci indique un environnement de DÉVELOPPEMENT, pas de production."
    echo "   Ce script est conçu pour la production."
    echo ""
    read -p "Voulez-vous continuer quand même ? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# 2. Vérifier que les conteneurs tournent
echo "2. État des conteneurs Docker"
echo "------------------------------"
BACKEND_RUNNING=$(docker ps --filter "name=planflan-container-backend" --filter "status=running" -q)
NGINX_RUNNING=$(docker ps --filter "name=planflan-container-nginx" --filter "status=running" -q)

if [ -z "$BACKEND_RUNNING" ]; then
    echo -e "${RED}✗ Le conteneur backend n'est PAS en cours d'exécution${NC}"
    echo "  Démarrez-le avec: docker compose up -d planflan-backend"
    exit 1
else
    echo -e "${GREEN}✓ Backend actif${NC}"
fi

if [ -z "$NGINX_RUNNING" ]; then
    echo -e "${RED}✗ Le conteneur nginx n'est PAS en cours d'exécution${NC}"
else
    echo -e "${GREEN}✓ Nginx actif${NC}"
fi
echo ""

# 3. Vérifier la clé API Google Maps
echo "3. Clé API Google Maps"
echo "----------------------"
API_KEY_IN_ENV=$(grep "GOOGLE_MAPS_API_KEY" .env 2>/dev/null | cut -d'=' -f2 | tr -d ' ')
API_KEY_IN_CONTAINER=$(docker exec planflan-container-backend printenv GOOGLE_MAPS_API_KEY 2>/dev/null)

if [ -z "$API_KEY_IN_ENV" ]; then
    echo -e "${RED}✗ GOOGLE_MAPS_API_KEY non trouvée dans .env${NC}"
elif [ -z "$API_KEY_IN_CONTAINER" ]; then
    echo -e "${RED}✗ GOOGLE_MAPS_API_KEY non chargée dans le conteneur${NC}"
    echo "  La clé est dans .env mais pas dans le conteneur !"
    echo "  Redémarrez le conteneur : docker compose restart planflan-backend"
else
    KEY_LENGTH=${#API_KEY_IN_CONTAINER}
    echo -e "${GREEN}✓ Clé API définie et chargée (${KEY_LENGTH} caractères)${NC}"
    echo "  Début de la clé: ${API_KEY_IN_CONTAINER:0:15}..."
fi
echo ""

# 4. Tester l'accès à l'API Google depuis le conteneur
echo "4. Test de connectivité API Google"
echo "-----------------------------------"
echo "Test 1: Accès général à maps.googleapis.com"
GOOGLE_ACCESS=$(docker exec planflan-container-backend curl -s -o /dev/null -w "%{http_code}" https://maps.googleapis.com/ 2>/dev/null)
if [ "$GOOGLE_ACCESS" = "200" ] || [ "$GOOGLE_ACCESS" = "301" ] || [ "$GOOGLE_ACCESS" = "302" ]; then
    echo -e "${GREEN}✓ Accès à Google Maps API OK (HTTP $GOOGLE_ACCESS)${NC}"
else
    echo -e "${RED}✗ Problème d'accès à Google Maps API (HTTP $GOOGLE_ACCESS)${NC}"
    echo "  Le pare-feu du serveur bloque peut-être les connexions sortantes."
fi

if [ -n "$API_KEY_IN_CONTAINER" ]; then
    echo ""
    echo "Test 2: Appel API Places avec votre clé"
    # Test avec un place_id connu (Google Sydney Office)
    TEST_PLACE_ID="ChIJN1t_tDeuEmsRUsoyG83frY4"
    API_RESPONSE=$(docker exec planflan-container-backend curl -s \
        "https://maps.googleapis.com/maps/api/place/details/json?place_id=${TEST_PLACE_ID}&fields=photos&key=${API_KEY_IN_CONTAINER}")

    API_STATUS=$(echo "$API_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'UNKNOWN'))" 2>/dev/null)

    if [ "$API_STATUS" = "OK" ]; then
        echo -e "${GREEN}✓ Clé API valide et fonctionnelle${NC}"
        PHOTO_COUNT=$(echo "$API_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('result', {}).get('photos', [])))" 2>/dev/null)
        echo "  L'API retourne $PHOTO_COUNT photo(s) pour le lieu de test"
    elif [ "$API_STATUS" = "REQUEST_DENIED" ]; then
        echo -e "${RED}✗ Requête refusée par Google (REQUEST_DENIED)${NC}"
        echo "  CAUSE PROBABLE: Restrictions sur la clé API"
        echo ""
        echo "  Actions à effectuer dans Google Cloud Console:"
        echo "  1. Aller sur https://console.cloud.google.com/apis/credentials"
        echo "  2. Cliquer sur votre clé API"
        echo "  3. Vérifier 'API restrictions' → Places API doit être activée"
        echo "  4. Vérifier 'Application restrictions':"
        echo "     - Option 'None' (recommandé pour tester)"
        echo "     - OU 'HTTP referrers' avec: planflan.fr/*, *.planflan.fr/*"
        ERROR_MSG=$(echo "$API_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error_message', 'N/A'))" 2>/dev/null)
        echo "  Message d'erreur Google: $ERROR_MSG"
    else
        echo -e "${YELLOW}⚠️  Statut API inattendu: $API_STATUS${NC}"
        echo "  Réponse complète:"
        echo "$API_RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
    fi
fi
echo ""

# 5. Vérifier le niveau de logs
echo "5. Configuration des logs"
echo "-------------------------"
LOG_LEVEL=$(docker exec planflan-container-backend python -c "
import os
os.environ['FLASK_CONFIG'] = 'ConfigProd'
from app import create_app
app = create_app()
with app.app_context():
    print(app.config.get('LOG_LEVEL', 'N/A'))
" 2>/dev/null)

if [ "$LOG_LEVEL" = "WARNING" ] || [ "$LOG_LEVEL" = "ERROR" ]; then
    echo -e "${YELLOW}⚠️  LOG_LEVEL = $LOG_LEVEL${NC}"
    echo "   Les logs INFO de FETCH_PHOTOS ne seront PAS visibles."
    echo "   Pour déboguer, changez temporairement dans app/configprod.py:"
    echo "   LOG_LEVEL = 'INFO'"
    echo "   Puis redémarrez: docker compose restart planflan-backend"
elif [ "$LOG_LEVEL" = "INFO" ] || [ "$LOG_LEVEL" = "DEBUG" ]; then
    echo -e "${GREEN}✓ LOG_LEVEL = $LOG_LEVEL (les logs FETCH_PHOTOS seront visibles)${NC}"
else
    echo -e "${YELLOW}⚠️  LOG_LEVEL = $LOG_LEVEL (valeur inattendue)${NC}"
fi
echo ""

# 6. Analyser les logs FETCH_PHOTOS récents
echo "6. Logs FETCH_PHOTOS récents"
echo "----------------------------"
FETCH_LOGS=$(docker logs planflan-container-backend 2>&1 | grep "FETCH_PHOTOS" | tail -20)

if [ -z "$FETCH_LOGS" ]; then
    echo -e "${YELLOW}⚠️  Aucun log FETCH_PHOTOS trouvé${NC}"
    echo "   Causes possibles:"
    echo "   1. Aucun établissement avec google_place_id n'a été créé récemment"
    echo "   2. LOG_LEVEL est trop élevé (WARNING au lieu de INFO)"
    echo "   3. Le code fetch_place_photos() n'est jamais appelé"
else
    echo -e "${GREEN}✓ Logs FETCH_PHOTOS trouvés:${NC}"
    echo "$FETCH_LOGS"
    echo ""

    # Analyser les erreurs courantes
    if echo "$FETCH_LOGS" | grep -q "Aucune photo trouvée dans les détails"; then
        echo -e "${RED}✗ ERREUR DÉTECTÉE: 'Aucune photo trouvée'${NC}"
        echo "   → L'API Google ne retourne pas de photos"
        echo "   → Vérifiez les restrictions de la clé API (voir section 4)"
    fi

    if echo "$FETCH_LOGS" | grep -q "status=403"; then
        echo -e "${RED}✗ ERREUR DÉTECTÉE: HTTP 403${NC}"
        echo "   → La clé API est refusée par Google"
        echo "   → Vérifiez les restrictions dans Google Cloud Console"
    fi

    if echo "$FETCH_LOGS" | grep -q "Pas de permission d'écriture"; then
        echo -e "${RED}✗ ERREUR DÉTECTÉE: Pas de permission d'écriture${NC}"
        echo "   → Voir section 7 pour corriger les permissions"
    fi

    if echo "$FETCH_LOGS" | grep -q "Fichier créé avec succès"; then
        echo -e "${GREEN}✓ Les photos SONT téléchargées avec succès${NC}"
        echo "   → Le problème est peut-être dans l'affichage (nginx ou frontend)"
    fi
fi
echo ""

# 7. Vérifier le dossier uploads et permissions
echo "7. Dossier uploads et permissions"
echo "----------------------------------"
UPLOADS_EXISTS=$(docker exec planflan-container-backend test -d /app/static/uploads && echo "yes" || echo "no")

if [ "$UPLOADS_EXISTS" = "yes" ]; then
    echo -e "${GREEN}✓ Dossier /app/static/uploads existe${NC}"

    # Lister le contenu
    echo ""
    echo "Contenu du dossier:"
    docker exec planflan-container-backend ls -lah /app/static/uploads/ 2>/dev/null | head -10

    # Compter les photos
    JPG_COUNT=$(docker exec planflan-container-backend find /app/static/uploads -name "*.jpg" 2>/dev/null | wc -l)
    echo ""
    echo "Nombre de fichiers .jpg: $JPG_COUNT"

    # Test d'écriture
    echo ""
    echo "Test d'écriture:"
    if docker exec planflan-container-backend touch /app/static/uploads/test_diagnostic.txt 2>/dev/null; then
        echo -e "${GREEN}✓ Écriture possible${NC}"
        docker exec planflan-container-backend rm /app/static/uploads/test_diagnostic.txt 2>/dev/null
    else
        echo -e "${RED}✗ Impossible d'écrire dans le dossier${NC}"
        echo "  Correction: docker exec planflan-container-backend chmod -R 777 /app/static/uploads"
    fi
else
    echo -e "${RED}✗ Dossier /app/static/uploads n'existe pas${NC}"
    echo "  Création: docker exec planflan-container-backend mkdir -p /app/static/uploads"
    echo "  Permissions: docker exec planflan-container-backend chmod -R 777 /app/static/uploads"
fi
echo ""

# 8. Vérifier l'accès nginx au volume
echo "8. Volume photos dans nginx"
echo "---------------------------"
if [ -n "$NGINX_RUNNING" ]; then
    NGINX_UPLOADS=$(docker exec planflan-container-nginx test -d /var/www/uploads && echo "yes" || echo "no")

    if [ "$NGINX_UPLOADS" = "yes" ]; then
        echo -e "${GREEN}✓ Nginx a accès à /var/www/uploads${NC}"

        # Comparer le nombre de fichiers
        NGINX_JPG_COUNT=$(docker exec planflan-container-nginx find /var/www/uploads -name "*.jpg" 2>/dev/null | wc -l)
        echo "  Fichiers .jpg visibles par nginx: $NGINX_JPG_COUNT"

        if [ "$JPG_COUNT" != "$NGINX_JPG_COUNT" ]; then
            echo -e "${RED}✗ Incohérence: backend ($JPG_COUNT) vs nginx ($NGINX_JPG_COUNT)${NC}"
            echo "  Le volume n'est peut-être pas correctement partagé."
        fi
    else
        echo -e "${RED}✗ Nginx n'a PAS accès à /var/www/uploads${NC}"
        echo "  Le volume photos_volume n'est pas correctement monté dans nginx."
        echo "  Vérifiez docker-compose.yml section nginx > volumes"
    fi
fi
echo ""

# 9. Vérifier la configuration nginx
echo "9. Configuration nginx"
echo "----------------------"
if [ -n "$NGINX_RUNNING" ]; then
    NGINX_CONF=$(docker exec planflan-container-nginx cat /etc/nginx/conf.d/default.conf 2>/dev/null | grep -A5 "location /static/uploads")

    if [ -n "$NGINX_CONF" ]; then
        echo -e "${GREEN}✓ Configuration /static/uploads/ trouvée:${NC}"
        echo "$NGINX_CONF"
    else
        echo -e "${RED}✗ Configuration /static/uploads/ MANQUANTE${NC}"
        echo "  nginx/default.conf doit contenir:"
        echo "  location /static/uploads/ {"
        echo "    alias /var/www/uploads/;"
        echo "    ..."
        echo "  }"
    fi
fi
echo ""

# 10. Test d'accès HTTP
echo "10. Test d'accès HTTP aux photos"
echo "---------------------------------"
if [ "$JPG_COUNT" -gt 0 ]; then
    FIRST_PHOTO=$(docker exec planflan-container-backend find /app/static/uploads -name "*.jpg" 2>/dev/null | head -1 | xargs basename)

    if [ -n "$FIRST_PHOTO" ]; then
        echo "Test avec la photo: $FIRST_PHOTO"
        echo ""

        # Test depuis le serveur
        echo "Depuis le serveur (via nginx):"
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/static/uploads/$FIRST_PHOTO 2>/dev/null)

        if [ "$HTTP_STATUS" = "200" ]; then
            echo -e "${GREEN}✓ HTTP $HTTP_STATUS - La photo est accessible localement${NC}"
        else
            echo -e "${RED}✗ HTTP $HTTP_STATUS - La photo n'est PAS accessible${NC}"
        fi

        # Test HTTPS depuis l'extérieur
        echo ""
        echo "Depuis l'extérieur (HTTPS):"
        echo "Testez manuellement: curl -I https://planflan.fr/static/uploads/$FIRST_PHOTO"
    fi
else
    echo -e "${YELLOW}⚠️  Aucune photo .jpg trouvée pour tester${NC}"
fi
echo ""

# 11. Vérifier la base de données
echo "11. Photos dans la base de données"
echo "-----------------------------------"
DB_PHOTOS=$(docker exec planflan-container-backend python -c "
from app import create_app, db
from app.models import Photo
app = create_app()
with app.app_context():
    count = Photo.query.count()
    print(f'{count}')
" 2>/dev/null)

if [ -n "$DB_PHOTOS" ]; then
    if [ "$DB_PHOTOS" -gt 0 ]; then
        echo -e "${GREEN}✓ $DB_PHOTOS photo(s) enregistrée(s) en base${NC}"
    else
        echo -e "${YELLOW}⚠️  Aucune photo en base de données${NC}"
        echo "   Les photos ne sont jamais téléchargées."
    fi
else
    echo -e "${YELLOW}⚠️  Impossible de vérifier la base de données${NC}"
fi
echo ""

# RÉSUMÉ FINAL
echo "=========================================="
echo "RÉSUMÉ ET RECOMMANDATIONS"
echo "=========================================="
echo ""

# Diagnostic automatique
ISSUES_FOUND=0

if [ -z "$API_KEY_IN_CONTAINER" ]; then
    echo -e "${RED}❌ Clé API non chargée${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
elif [ "$API_STATUS" = "REQUEST_DENIED" ]; then
    echo -e "${RED}❌ Clé API refusée - VÉRIFIER LES RESTRICTIONS${NC}"
    echo "   🔧 Action: Console Google Cloud → Retirer les restrictions"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if [ "$LOG_LEVEL" = "WARNING" ] && [ -z "$FETCH_LOGS" ]; then
    echo -e "${YELLOW}⚠️  Logs masqués - Impossible de diagnostiquer${NC}"
    echo "   🔧 Action: Changer LOG_LEVEL='INFO' dans app/configprod.py"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if [ "$UPLOADS_EXISTS" = "no" ]; then
    echo -e "${RED}❌ Dossier uploads manquant${NC}"
    echo "   🔧 Action: mkdir -p /app/static/uploads && chmod 777 /app/static/uploads"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if [ "$NGINX_UPLOADS" = "no" ]; then
    echo -e "${RED}❌ Volume non accessible par nginx${NC}"
    echo "   🔧 Action: Vérifier docker-compose.yml et redémarrer"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if [ "$ISSUES_FOUND" -eq 0 ]; then
    echo -e "${GREEN}✅ Aucun problème évident détecté${NC}"
    echo ""
    echo "Si les photos ne s'affichent toujours pas:"
    echo "1. Activez les logs INFO et créez un nouvel établissement"
    echo "2. Suivez les logs en temps réel:"
    echo "   docker logs -f planflan-container-backend | grep FETCH_PHOTOS"
    echo "3. Partagez la sortie complète pour un diagnostic approfondi"
else
    echo ""
    echo -e "${RED}$ISSUES_FOUND problème(s) détecté(s)${NC}"
    echo "Corrigez les problèmes ci-dessus et relancez ce script."
fi

echo ""
echo "=========================================="
echo "Documentation complète: DIAGNOSTIC_PHOTOS_PRODUCTION.md"
echo "=========================================="

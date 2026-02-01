#!/bin/bash
# Script de diagnostic pour identifier les différences entre Docker local et production
# concernant le téléchargement et l'affichage des photos Google Places

echo "=========================================="
echo "DIAGNOSTIC PHOTOS - LOCAL vs PRODUCTION"
echo "=========================================="
echo ""

# 1. Vérifier la configuration actuelle
echo "1. Configuration actuelle"
echo "-------------------------"
if [ -f "docker-compose.override.yml" ]; then
    echo "✓ Mode LOCAL détecté (docker-compose.override.yml présent)"
    MODE="local"
else
    echo "✓ Mode PRODUCTION détecté (pas de docker-compose.override.yml)"
    MODE="production"
fi
echo ""

# 2. Vérifier que les conteneurs tournent
echo "2. État des conteneurs"
echo "----------------------"
docker compose ps
echo ""

# 3. Vérifier la clé API Google Maps
echo "3. Clé API Google Maps"
echo "----------------------"
if [ -f ".env" ]; then
    GOOGLE_KEY=$(grep "GOOGLE_MAPS_API_KEY" .env | cut -d'=' -f2)
    if [ -z "$GOOGLE_KEY" ]; then
        echo "✗ GOOGLE_MAPS_API_KEY non définie dans .env"
    else
        KEY_LENGTH=${#GOOGLE_KEY}
        echo "✓ GOOGLE_MAPS_API_KEY définie (longueur: $KEY_LENGTH caractères)"
        echo "  Début de la clé: ${GOOGLE_KEY:0:10}..."
    fi
else
    echo "✗ Fichier .env introuvable"
fi
echo ""

# 4. Vérifier les logs du backend pour FETCH_PHOTOS
echo "4. Logs FETCH_PHOTOS du backend"
echo "--------------------------------"
echo "Dernières entrées FETCH_PHOTOS:"
docker logs planflan-container-backend 2>&1 | grep "FETCH_PHOTOS" | tail -20
if [ $? -ne 0 ]; then
    echo "Aucun log FETCH_PHOTOS trouvé"
fi
echo ""

# 5. Vérifier l'accès au dossier uploads dans le conteneur
echo "5. Dossier uploads dans le conteneur"
echo "-------------------------------------"
echo "Contenu de /app/static/uploads:"
docker exec planflan-container-backend ls -lah /app/static/uploads/ 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ Impossible d'accéder au dossier uploads"
else
    echo ""
    echo "Test d'écriture:"
    docker exec planflan-container-backend touch /app/static/uploads/test_diagnostic.txt 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ Écriture possible dans /app/static/uploads"
        docker exec planflan-container-backend rm /app/static/uploads/test_diagnostic.txt
    else
        echo "✗ Impossible d'écrire dans /app/static/uploads"
    fi
fi
echo ""

# 6. Vérifier la configuration UPLOAD_FOLDER
echo "6. Configuration UPLOAD_FOLDER"
echo "------------------------------"
docker exec planflan-container-backend python -c "
import os
os.environ['FLASK_CONFIG'] = 'ConfigProd'
from app import create_app
app = create_app()
with app.app_context():
    print(f'UPLOAD_FOLDER: {app.config[\"UPLOAD_FOLDER\"]}')
    print(f'Existe: {os.path.exists(app.config[\"UPLOAD_FOLDER\"])}')
    print(f'Écriture: {os.access(app.config[\"UPLOAD_FOLDER\"], os.W_OK)}')
" 2>&1
echo ""

# 7. Vérifier le volume photos_volume
echo "7. Volume Docker photos_volume"
echo "------------------------------"
docker volume inspect planflan2_photos_volume 2>/dev/null | grep -A2 "Mountpoint"
if [ $? -ne 0 ]; then
    echo "✗ Volume photos_volume introuvable"
fi
echo ""

# 8. Vérifier la configuration nginx
echo "8. Configuration nginx pour /static/uploads/"
echo "--------------------------------------------"
if [ "$MODE" = "local" ]; then
    echo "Configuration utilisée: nginx/default.dev.conf"
    grep -A3 "location /static/uploads/" nginx/default.dev.conf
else
    echo "Configuration utilisée: nginx/default.conf"
    grep -A3 "location /static/uploads/" nginx/default.conf
fi
echo ""

# 9. Vérifier l'accès nginx au volume
echo "9. Volume uploads dans nginx"
echo "----------------------------"
docker exec planflan-container-nginx ls -lah /var/www/uploads/ 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ Nginx ne peut pas accéder à /var/www/uploads/"
else
    echo "✓ Nginx peut accéder à /var/www/uploads/"
fi
echo ""

# 10. Tester une photo existante
echo "10. Test d'accès à une photo"
echo "----------------------------"
FIRST_PHOTO=$(docker exec planflan-container-backend ls /app/static/uploads/*.jpg 2>/dev/null | head -1 | xargs basename)
if [ -n "$FIRST_PHOTO" ]; then
    echo "Photo testée: $FIRST_PHOTO"
    if [ "$MODE" = "local" ]; then
        curl -I http://localhost:81/static/uploads/$FIRST_PHOTO 2>&1 | head -5
    else
        echo "En production, testez: curl -I https://planflan.fr/static/uploads/$FIRST_PHOTO"
    fi
else
    echo "Aucune photo .jpg trouvée dans uploads"
fi
echo ""

# 11. Vérifier les logs d'erreur récents
echo "11. Erreurs récentes du backend"
echo "--------------------------------"
docker logs planflan-container-backend 2>&1 | grep -i "error\|erreur\|exception" | tail -10
echo ""

# 12. Résumé
echo "=========================================="
echo "RÉSUMÉ DU DIAGNOSTIC"
echo "=========================================="
echo "Mode: $MODE"
echo ""
echo "Points à vérifier:"
echo "- La clé API Google Maps est-elle valide?"
echo "- Les logs FETCH_PHOTOS montrent-ils des erreurs?"
echo "- Le dossier /app/static/uploads est-il accessible en écriture?"
echo "- Nginx peut-il servir les fichiers depuis /var/www/uploads/?"
echo "- Les photos sont-elles bien téléchargées mais pas affichées?"
echo ""
echo "Pour plus de détails, consultez:"
echo "  docker logs planflan-container-backend"
echo "  docker logs planflan-container-nginx"

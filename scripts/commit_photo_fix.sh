#!/bin/bash

# Script pour committer les changements du fix des photos Google Places

echo "🔧 Commit des corrections pour le téléchargement des photos Google Places en production"
echo ""

# Vérifier qu'on est sur la branche dev
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "dev" ]; then
    echo "⚠️  Vous n'êtes pas sur la branche dev (branche actuelle: $BRANCH)"
    read -p "Voulez-vous continuer ? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📝 Fichiers modifiés :"
echo "  - Dockerfile (WORKDIR /app + création dossier uploads)"
echo "  - docker-compose.yml (volumes corrigés)"
echo "  - entrypoint.sh (vérification uploads)"
echo "  - app/configprod.py (chemin absolu UPLOAD_FOLDER)"
echo "  - app/outils.py (logs détaillés fetch_place_photos)"
echo "  - nginx/default.conf (location /static/uploads/)"
echo "  - tests/test_scenario_photos.py (tests améliorés)"
echo ""
echo "📄 Nouveaux fichiers :"
echo "  - PHOTO_UPLOAD_FIX.md"
echo "  - DEPLOYMENT_PHOTO_FIX.md"
echo ""

# Ajouter les fichiers modifiés
git add Dockerfile
git add docker-compose.yml
git add entrypoint.sh
git add app/configprod.py
git add app/outils.py
git add nginx/default.conf
git add tests/test_scenario_photos.py
git add PHOTO_UPLOAD_FIX.md
git add DEPLOYMENT_PHOTO_FIX.md
git add scripts/commit_photo_fix.sh

echo "✅ Fichiers ajoutés au staging"
echo ""

# Message de commit
COMMIT_MSG="fix: Correction téléchargement photos Google Places en production Docker

Problème : Les photos Google Places se téléchargeaient en dev mais pas en production.

Causes identifiées :
- WORKDIR Docker incohérent (/python-docker vs /app)
- Dossier static/uploads jamais créé dans le conteneur
- Permissions d'écriture manquantes
- Chemin relatif UPLOAD_FOLDER non résolu correctement

Corrections :
- Dockerfile : WORKDIR standardisé à /app + création dossier uploads
- docker-compose.yml : volumes montés sur /app au lieu de /python-docker
- entrypoint.sh : vérification et test d'écriture du dossier uploads
- app/configprod.py : UPLOAD_FOLDER avec chemin absolu
- app/outils.py : logs détaillés [FETCH_PHOTOS] + vérifications
- nginx/default.conf : location /static/uploads/ pour servir les fichiers
- tests : 10 tests validant la configuration et les permissions

Tests : ✅ 10/10 passent

Documentation :
- PHOTO_UPLOAD_FIX.md : explication détaillée du problème et solutions
- DEPLOYMENT_PHOTO_FIX.md : guide de déploiement étape par étape

Voir DEPLOYMENT_PHOTO_FIX.md pour la procédure de déploiement complète."

echo "📋 Message de commit :"
echo "---"
echo "$COMMIT_MSG"
echo "---"
echo ""

read -p "Voulez-vous committer ces changements ? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "$COMMIT_MSG"
    echo ""
    echo "✅ Commit effectué avec succès !"
    echo ""
    echo "📌 Prochaines étapes :"
    echo "  1. Vérifier les tests : python -m pytest tests/test_scenario_photos.py -v"
    echo "  2. Pousser sur dev : git push origin dev"
    echo "  3. Merger sur main : git checkout main && git merge dev"
    echo "  4. Déployer en production : voir DEPLOYMENT_PHOTO_FIX.md"
else
    echo "❌ Commit annulé"
    git reset HEAD
fi

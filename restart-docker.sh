#!/bin/bash

# Script pour redémarrer Docker avec la nouvelle configuration

cd /home/damien/PycharmProjects/planflan2

echo "Arrêt des conteneurs..."
docker compose down

echo "Démarrage des conteneurs..."
docker compose up -d

echo "Attente du démarrage..."
sleep 5

echo "État des conteneurs :"
docker compose ps

echo ""
echo "Test de l'image :"
curl -I http://localhost:81/static/uploads/ChIJ4xutfT5u5kcRaJn2NkiOhPU_photo_0.jpg

echo ""
echo "Logs nginx :"
docker compose logs nginx | tail -10

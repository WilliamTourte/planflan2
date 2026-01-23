#!/bin/bash

# Script pour configurer et exécuter les tests JavaScript

echo "🚀 Configuration des tests JavaScript pour PlanFlan"
echo ""

# Vérifier si Node.js est installé
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé. Veuillez installer Node.js d'abord."
    echo ""
    echo "Sur Ubuntu/Debian :"
    echo "  sudo apt update"
    echo "  sudo apt install -y nodejs npm"
    echo ""
    echo "Ou via nvm (recommandé) :"
    echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash"
    echo "  source ~/.bashrc"
    echo "  nvm install --lts"
    echo ""
    exit 1
fi

# Vérifier si npm est installé
if ! command -v npm &> /dev/null; then
    echo "❌ npm n'est pas installé. Veuillez installer npm."
    exit 1
fi

echo "✅ Node.js et npm sont installés"
echo "   Node.js version: $(node --version)"
echo "   npm version: $(npm --version)"
echo ""

# Installer les dépendances
if [ -f "package-lock.json" ]; then
    echo "📦 Installation des dépendances depuis package-lock.json..."
    npm ci
else
    echo "📦 Installation des dépendances..."
    npm install
fi

if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation des dépendances"
    exit 1
fi

echo "✅ Dépendances installées avec succès"
echo ""

# Exécuter les tests
if [ "$1" = "watch" ]; then
    echo "👀 Exécution des tests en mode watch..."
    npm run test:watch
elif [ "$1" = "unit" ]; then
    echo "🧪 Exécution des tests unitaires..."
    npm run test:unit
elif [ "$1" = "integration" ]; then
    echo "🔗 Exécution des tests d'intégration..."
    npm run test:integration
else
    echo "🧪 Exécution de tous les tests..."
    npm test
fi

echo ""
echo "🎉 Configuration des tests JavaScript terminée !"
echo ""
echo "Commandes disponibles :"
echo "  npm test              # Exécuter tous les tests"
echo "  npm run test:watch    # Mode watch (développement)"
echo "  npm run test:unit     # Tests unitaires uniquement"
echo "  npm run test:integration # Tests d'intégration uniquement"
echo "  npm run lint          # Vérifier la qualité du code"
echo "  npm run lint:fix      # Corriger automatiquement les problèmes"

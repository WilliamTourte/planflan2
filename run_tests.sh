#!/bin/bash

# Script d'automatisation des tests pour PlanFlan
# Utilisation: ./run_tests.sh [options]
# Options:
#   --all       Exécuter tous les tests (défaut)
#   --forms     Exécuter uniquement les tests de formulaires
#   --coverage  Générer un rapport de coverage
#   --html      Générer un rapport HTML de coverage
#   --help      Afficher cette aide

set -e  # Quitter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# Fonction pour afficher l'aide
show_help() {
    echo "Utilisation: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --all       Exécuter tous les tests (défaut)"
    echo "  --forms     Exécuter uniquement les tests de formulaires"
    echo "  --coverage  Générer un rapport de coverage"
    echo "  --html      Générer un rapport HTML de coverage"
    echo "  --help      Afficher cette aide"
    exit 0
}

# Vérifier si pytest est installé
check_pytest() {
    if ! command -v pytest &> /dev/null; then
        echo -e "${RED}Erreur: pytest n'est pas installé.${NC}"
        echo "Installation: pip install pytest"
        exit 1
    fi
}

# Vérifier si pytest-cov est installé
check_pytest_cov() {
    if ! python -c "import pytest_cov" 2>/dev/null; then
        echo -e "${RED}Erreur: pytest-cov n'est pas installé.${NC}"
        echo "Installation: pip install pytest-cov"
        exit 1
    fi
}

# Exécuter les tests de formulaires
test_forms() {
    echo -e "${YELLOW}Exécution des tests de formulaires...${NC}"
    export PYTHONPATH=$(pwd):$PYTHONPATH
    if [ "$COVERAGE" = true ]; then
        if [ "$HTML" = true ]; then
            pytest tests/test_forms.py --cov=app --cov-report=html --cov-report=term
        else
            pytest tests/test_forms.py --cov=app --cov-report=term
        fi
    else
        pytest tests/test_forms.py -v
    fi
}

# Exécuter tous les tests
test_all() {
    echo -e "${YELLOW}Exécution de tous les tests...${NC}"
    export PYTHONPATH=$(pwd):$PYTHONPATH
    if [ "$COVERAGE" = true ]; then
        if [ "$HTML" = true ]; then
            pytest tests/ --cov=app --cov-report=html --cov-report=term
        else
            pytest tests/ --cov=app --cov-report=term
        fi
    else
        pytest tests/ -v
    fi
}

# Parser les arguments
COVERAGE=false
HTML=false
TARGET="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        --forms)
            TARGET="forms"
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --html)
            HTML=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo -e "${RED}Option inconnue: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Vérifier les dépendances
check_pytest
if [ "$COVERAGE" = true ]; then
    check_pytest_cov
fi

# Exécuter les tests appropriés
if [ "$TARGET" = "forms" ]; then
    test_forms
else
    test_all
fi

# Vérifier le résultat
echo ""
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les tests ont passé avec succès !${NC}"
else
    echo -e "${RED}❌ Certains tests ont échoué.${NC}"
    exit 1
fi
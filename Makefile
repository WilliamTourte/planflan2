# Makefile pour l'automatisation des tests et du déploiement

.PHONY: help test test-forms test-coverage test-html lint format clean

# Affiche l'aide
help:
	@echo "Makefile pour PlanFlan - Automatisation des tests"
	@echo ""
	@echo "Cibles disponibles:"
	@echo "  help              Affiche cette aide"
	@echo "  test              Exécute tous les tests"
	@echo "  test-forms        Exécute uniquement les tests de formulaires"
	@echo "  test-coverage     Exécute les tests avec coverage"
	@echo "  test-html         Exécute les tests avec rapport HTML de coverage"
	@echo "  lint              Vérifie la qualité du code (à configurer)"
	@echo "  format            Formate le code (à configurer)"
	@echo "  clean             Nettoie les fichiers temporaires"
	@echo ""

# Exécute tous les tests
test:
	@echo "🧪 Exécution de tous les tests..."
	PYTHONPATH=$(CURDIR) pytest tests/ -v

# Exécute uniquement les tests de formulaires
test-forms:
	@echo "📝 Exécution des tests de formulaires..."
	PYTHONPATH=$(CURDIR) pytest tests/test_forms.py -v

# Exécute les tests avec coverage
test-coverage:
	@echo "📊 Exécution des tests avec coverage..."
	PYTHONPATH=$(CURDIR) pytest tests/ --cov=app --cov-report=term

# Exécute les tests avec rapport HTML de coverage
test-html:
	@echo "📊 Exécution des tests avec rapport HTML de coverage..."
	PYTHONPATH=$(CURDIR) pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "📁 Rapport généré dans htmlcov/index.html"

# Vérifie la qualité du code (à configurer selon vos outils)
lint:
	@echo "🔍 Vérification de la qualité du code..."
	# flake8 app/ tests/
	# pylint app/ tests/
	@echo "⚠️  À configurer avec vos outils de linting"

# Formate le code (à configurer selon vos outils)
format:
	@echo "🎨 Formatage du code..."
	# black app/ tests/
	# isort app/ tests/
	@echo "⚠️  À configurer avec vos outils de formatage"

# Nettoie les fichiers temporaires
clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf app/__pycache__
	rm -rf tests/__pycache__
	rm -rf .coverage
	rm -rf htmlcov
	@echo "✅ Nettoyage terminé"

# Cible par défaut
default: help
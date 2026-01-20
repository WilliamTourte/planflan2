# Makefile pour PlanFlan - Commandes de test optimisées

.PHONY: test, test-quick, test-auth, test-admin, test-critical, test-slow, test-all

# Exécuter tous les tests (complet, pour CI/CD)
test-all:
	python -m pytest tests/ -v -n auto

# Exécuter les tests critiques seulement (pour développement rapide)
test-critical:
	python -m pytest tests/ -m "critical" -v -n auto

# Exécuter les tests d'authentification (tous les fichiers)
test-all-auth:
	python -m pytest tests/ -m "auth" -v

# Exécuter les tests d'authentification seulement
test-auth:
	python -m pytest tests/test_securite.py -m "auth" -v

# Exécuter les tests d'administration seulement
test-admin:
	python -m pytest tests/test_securite.py tests/test_auth.py -m "admin" -v

# Exécuter les tests principaux seulement
test-main:
	python -m pytest tests/test_main.py -m "main" -v

# Exécuter les tests de formulaires seulement
test-forms:
	python -m pytest tests/test_forms.py -m "forms" -v

# Exécuter les tests d'outils seulement
test-utils:
	python -m pytest tests/test_outils.py -m "utils" -v

# Exécuter les tests de carte seulement
test-maps:
	python -m pytest tests/test_maps.py -m "maps" -v

# Exécuter les tests de scénarios seulement
test-scenarios:
	python -m pytest tests/test_scenarios.py -m "scenarios" -v

# Exécuter les tests unitaires seulement
test-unitary:
	python -m pytest tests/test_main_unitary.py -m "unitary" -v

# Exécuter les tests d'application seulement
test-app:
	python -m pytest tests/test_app.py -m "app" -v

# Exécuter les tests lents (API, upload, etc.)
test-slow:
	python -m pytest tests/test_securite.py -m "slow" -v

# Exécuter les tests rapides (pour développement quotidien)
test-quick:
	python -m pytest tests/ -m "critical and not slow" -v

# Exécuter un test spécifique
test-specific:
	@echo "Usage: make test-specific TEST=test_nom_du_test"
	python -m pytest tests/test_securite.py::$(TEST) -v

# Voir la liste des tests disponibles
test-list:
	python -m pytest tests/test_securite.py --collect-only -v

# Exécuter les tests avec coverage
test-coverage:
	python -m pytest tests/ -n auto --cov=app --cov-report=html -v

# Exécuter les tests critiques avec coverage
test-critical-coverage:
	python -m pytest tests/ -m "critical" --cov=app --cov-report=html -v

# Exécuter les tests avec coverage complet (tous les tests)
test-full-coverage:
	python -m pytest tests/ -n auto --cov=app --cov-report=html --cov-report=term --cov-report=xml -v

# Exécuter les tests pour CI/CD (optimisé pour les pipelines)
test-ci:
	python -m pytest tests/ --cov=app --cov-report=xml --cov-report=term -v --tb=short

# Exécuter les tests de smoke (rapides pour vérification basique)
test-smoke:
	python -m pytest tests/ -m "smoke" -v --tb=short

# Exécuter les tests de régression (complets pour CI)
test-regression:
	python -m pytest tests/ -m "regression" -v --tb=short

# Exécuter les tests end-to-end (scénarios utilisateurs)
test-e2e:
	python -m pytest tests/ -m "e2e or integration" -v --tb=short

# Exécuter les tests d'API seulement
test-api:
	python -m pytest tests/ -m "api" -v --tb=short

# Exécuter les tests de déploiement (nécessite l'accès au site en production)
test-deployment:
	RUN_DEPLOYMENT_TESTS=true python -m pytest tests/test_deployment.py -v --tb=short

# Exécuter les tests de base de données seulement
test-database:
	python -m pytest tests/ -m "database" -v --tb=short

# Exécuter les tests sans les lents (pour développement)
test-without-slow:
	python -m pytest tests/ -m "not slow" -v --tb=short

# Exécuter uniquement les tests critiques et smoke
test-critical-smoke:
	python -m pytest tests/ -m "critical or smoke" -v --tb=short

# Exécuter les tests avec parallelisation optimisée
test-parallel:
	python -m pytest tests/ -n auto --dist=loadfile -v --tb=short

# Exécuter les tests avec parallelisation optimisée (sans les lents)
test-parallel-quick:
	python -m pytest tests/ -m "not slow" -n auto --dist=loadfile -v --tb=short

# Générer uniquement le rapport HTML à partir du fichier .coverage existant
coverage-html:
	coverage html

# Nettoyer les anciens rapports de coverage
coverage-clean:
	rm -f .coverage htmlcov/*

# Voir le rapport de coverage textuel
coverage-report:
	coverage report

# Vérifier que le fichier XML de coverage existe pour CI
coverage-check-xml:
	@if [ -f "coverage.xml" ]; then \
        echo "✅ coverage.xml existe et est prêt pour CI"; \
        ls -lh coverage.xml; \
    else \
        echo "❌ coverage.xml est manquant!"; \
        exit 1; \
    fi
# Makefile pour PlanFlan - Commandes de test optimisées

.PHONY: test, test-quick, test-auth, test-admin, test-critical, test-slow, test-all

# Exécuter tous les tests (complet, pour CI/CD)
test-all:
	python -m pytest tests/ -v

# Exécuter les tests critiques seulement (pour développement rapide)
test-critical:
	python -m pytest tests/ -m "critical" -v

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
	python -m pytest tests/test_securite.py --cov=app --cov-report=html -v

# Exécuter les tests critiques avec coverage
test-critical-coverage:
	python -m pytest tests/test_securite.py -m "critical" --cov=app --cov-report=html -v
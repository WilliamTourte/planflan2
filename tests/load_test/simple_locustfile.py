from locust import HttpUser, task, between
import random
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class PlanFlanUser(HttpUser):
    """Utilisateur de base pour tester PlanFlan en environnement de développement"""
    wait_time = between(1, 3)  # Temps d'attente réaliste entre les actions

    # Villes disponibles dans votre base de données
    available_cities = ["Lyon", "Toulouse", "Paris"]

    def on_start(self):
        """Initialisation - vérification de la configuration"""
        # Déterminer le port automatiquement
        self.port = os.getenv("FLASK_RUN_PORT", "5000")
        self.host = f"http://localhost:{self.port}"
        print(f"Configuration: Tests exécutés sur {self.host}")

    @task(4)
    def load_homepage(self):
        """Test de chargement de la page d'accueil"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Échec chargement page d'accueil: {response.status_code}")
            else:
                # Vérification basique du contenu
                if b"PlanFlan" not in response.content:
                    response.failure("Contenu inattendu sur la page d'accueil")

    @task(6)
    def load_establishments_list(self):
        """Test de chargement de la liste des établissements"""
        with self.client.get("/liste_etablissements", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Échec chargement liste établissements: {response.status_code}")
            else:
                # Vérification basique du contenu
                content_check = b"etablissement" in response.content or b"etablissement" in response.content
                if not content_check:
                    response.failure("Contenu inattendu sur la page des établissements")

    @task(3)
    def browse_with_city_filter(self):
        """Test de navigation avec filtre par ville"""
        city = random.choice(self.available_cities)

        # Accès à la page d'accueil
        with self.client.get("/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Échec chargement page d'accueil: {response.status_code}")
                return

        # Accès à la liste avec filtre ville
        with self.client.get(f"/liste_etablissements?ville={city}", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Échec chargement avec filtre ville {city}: {response.status_code}")
            else:
                # Vérification que la ville apparaît dans la réponse
                if city.lower() not in response.text.lower():
                    response.failure(f"La ville {city} n'apparaît pas dans les résultats")

    @task(2)
    def test_api_endpoints(self):
        """Test des endpoints API utilisés par l'interface"""
        # Test de l'API villes (autocomplétion)
        test_city = random.choice(self.available_cities)[:3].lower()  # Prendre les 3 premières lettres

        with self.client.get(f"/api/villes?q={test_city}", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Échec API villes avec q={test_city}: {response.status_code}")
            else:
                try:
                    data = response.json()
                    if not isinstance(data, list):
                        response.failure("Réponse API villes non valide (pas une liste)")
                except:
                    response.failure("Réponse API villes non valide (pas du JSON)")

        # Test de l'API établissements
        with self.client.get("/api/etablissements?format=json&ville=Paris", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Échec API établissements: {response.status_code}")
            else:
                try:
                    data = response.json()
                    if not isinstance(data, list):
                        response.failure("Réponse API établissements non valide (pas une liste)")
                except:
                    response.failure("Réponse API établissements non valide (pas du JSON)")

    @task(1)
    def complete_browse_scenario(self):
        """Scénario complet: accueil -> liste -> détail (si disponible)"""
        # 1. Page d'accueil
        with self.client.get("/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Échec chargement page d'accueil: {response.status_code}")
                return

        # 2. Liste des établissements
        with self.client.get("/liste_etablissements", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Échec chargement liste: {response.status_code}")
                return

        # 3. Essayons d'accéder à un établissement si nous en trouvons un dans la réponse
        # (Cette partie est simplifiée - dans un vrai test, nous aurions des IDs connus)
        try:
            # Essayons de trouver un ID d'établissement dans le HTML
            content = response.text
            if "etablissement/" in content:
                # Simulation d'accès à un établissement (avec un ID fictif mais plausible)
                # Dans un environnement réel, nous utiliserions des IDs existants
                test_id = random.choice([1, 2, 3, 4, 5])  # IDs probables
                with self.client.get(f"/etablissement/{test_id}", catch_response=True) as response:
                    if response.status_code == 404:
                        # C'est normal si l'ID n'existe pas
                        pass
                    elif response.status_code != 200:
                        response.failure(f"Échec chargement établissement {test_id}: {response.status_code}")
        except:
            pass  # Ignorer les erreurs dans cette partie exploratoire
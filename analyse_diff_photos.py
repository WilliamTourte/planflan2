#!/usr/bin/env python3
"""
Script d'analyse des différences entre local et production pour les photos Google Places
"""

import os
import sys
from pathlib import Path

# Couleurs ANSI
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"  # No Color


def print_section(title):
    print(f"\n{BLUE}{'=' * 70}{NC}")
    print(f"{BLUE}{title}{NC}")
    print(f"{BLUE}{'=' * 70}{NC}\n")


def print_ok(msg):
    print(f"{GREEN}✓ {msg}{NC}")


def print_error(msg):
    print(f"{RED}✗ {msg}{NC}")


def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{NC}")


def print_info(msg):
    print(f"{CYAN}ℹ {msg}{NC}")


def check_env_file():
    """Vérifie le fichier .env"""
    print_section("1. VÉRIFICATION DU FICHIER .ENV")

    env_path = Path(".env")
    if not env_path.exists():
        print_error("Fichier .env introuvable")
        return False

    print_ok("Fichier .env trouvé")

    with open(env_path) as f:
        content = f.read()

    # Vérifier GOOGLE_MAPS_API_KEY
    if "GOOGLE_MAPS_API_KEY" in content:
        for line in content.split("\n"):
            if line.startswith("GOOGLE_MAPS_API_KEY"):
                key = line.split("=", 1)[1].strip().strip("\"'")
                if key:
                    print_ok(f"GOOGLE_MAPS_API_KEY définie (longueur: {len(key)} caractères)")
                    print_info(f"Préfixe: {key[:10]}...")
                    return True
                else:
                    print_error("GOOGLE_MAPS_API_KEY vide")
                    return False

    print_error("GOOGLE_MAPS_API_KEY non trouvée dans .env")
    return False


def check_config_files():
    """Vérifie les fichiers de configuration"""
    print_section("2. VÉRIFICATION DES FICHIERS DE CONFIGURATION")

    # app/config.py (local)
    config_local = Path("app/config.py")
    if config_local.exists():
        print_ok("app/config.py (local) trouvé")
        with open(config_local) as f:
            content = f.read()
            if "GOOGLE_MAPS_API_KEY" in content:
                print_ok("  - GOOGLE_MAPS_API_KEY configurée")
            if "UPLOAD_FOLDER" in content:
                # Extraire la valeur
                for line in content.split("\n"):
                    if "UPLOAD_FOLDER" in line and "=" in line:
                        upload_folder = line.split("=", 1)[1].strip().strip("\"'")
                        print_ok(f"  - UPLOAD_FOLDER = {upload_folder}")
            if "LOG_LEVEL" in content:
                for line in content.split("\n"):
                    if "LOG_LEVEL" in line and "=" in line:
                        log_level = line.split("=", 1)[1].strip().strip("\"'")
                        print_info(f"  - LOG_LEVEL = {log_level}")

    # app/configprod.py (production)
    config_prod = Path("app/configprod.py")
    if config_prod.exists():
        print_ok("app/configprod.py (production) trouvé")
        with open(config_prod) as f:
            content = f.read()
            if "GOOGLE_MAPS_API_KEY" in content:
                print_ok("  - GOOGLE_MAPS_API_KEY configurée")
            if "UPLOAD_FOLDER" in content:
                for line in content.split("\n"):
                    if "UPLOAD_FOLDER" in line and "=" in line and not line.strip().startswith("#"):
                        print_info(f"  - {line.strip()}")
            if "LOG_LEVEL" in content:
                log_levels = []
                for line in content.split("\n"):
                    if "LOG_LEVEL" in line and "=" in line and not line.strip().startswith("#"):
                        log_levels.append(line.strip())
                for log_line in log_levels:
                    if "WARNING" in log_line:
                        print_warning(
                            f"  - {log_line} ← ATTENTION: Les logs INFO ne seront pas visibles!"
                        )
                    else:
                        print_info(f"  - {log_line}")


def check_outils_py():
    """Vérifie le fichier app/outils.py"""
    print_section("3. VÉRIFICATION DE app/outils.py (fetch_place_photos)")

    outils_path = Path("app/outils.py")
    if not outils_path.exists():
        print_error("app/outils.py introuvable")
        return

    with open(outils_path) as f:
        content = f.read()

    # Vérifier la fonction fetch_place_photos
    if "def fetch_place_photos" in content:
        print_ok("Fonction fetch_place_photos trouvée")

        # Vérifier les logs
        log_count = content.count("[FETCH_PHOTOS]")
        print_info(f"  - {log_count} messages de log [FETCH_PHOTOS] dans le code")

        # Vérifier l'utilisation de logger.info
        info_count = content.count("logger.info")
        print_info(f"  - {info_count} appels à logger.info()")

        # Vérifier la gestion de UPLOAD_FOLDER
        if "UPLOAD_FOLDER" in content:
            print_ok("  - Utilise current_app.config['UPLOAD_FOLDER']")

        # Vérifier l'utilisation de l'API Google
        if "maps.googleapis.com/maps/api/place/photo" in content:
            print_ok("  - Appelle l'API Google Places pour les photos")

        if "maps.googleapis.com/maps/api/place/details" in content:
            print_ok("  - Appelle l'API Google Places pour les détails")


def check_routes_maps():
    """Vérifie le fichier app/routes/maps.py"""
    print_section("4. VÉRIFICATION DE app/routes/maps.py (ajouter_etablissement)")

    maps_path = Path("app/routes/maps.py")
    if not maps_path.exists():
        print_error("app/routes/maps.py introuvable")
        return

    with open(maps_path) as f:
        content = f.read()

    if "def ajouter_etablissement" in content:
        print_ok("Route ajouter_etablissement trouvée")

        # Vérifier l'appel à fetch_place_photos
        if "fetch_place_photos" in content:
            print_ok("  - Appelle fetch_place_photos()")

            # Compter les logs
            log_count = content.count("current_app.logger")
            print_info(f"  - {log_count} appels de logging dans le fichier")

            # Vérifier si google_place_id est utilisé
            if "google_place_id" in content:
                print_ok("  - Utilise google_place_id")
        else:
            print_error("  - N'appelle PAS fetch_place_photos() !")


def check_docker_config():
    """Vérifie la configuration Docker"""
    print_section("5. VÉRIFICATION DE LA CONFIGURATION DOCKER")

    # docker-compose.yml
    docker_compose = Path("docker-compose.yml")
    if docker_compose.exists():
        print_ok("docker-compose.yml trouvé")
        with open(docker_compose) as f:
            content = f.read()

        # Vérifier le volume uploads
        if "photos_volume:/app/static/uploads" in content:
            print_ok("  - Volume photos_volume monté sur /app/static/uploads (backend)")
        else:
            print_error("  - Volume uploads NON monté pour le backend")

        if "photos_volume:/var/www/uploads" in content:
            print_ok("  - Volume photos_volume monté sur /var/www/uploads (nginx)")
        else:
            print_error("  - Volume uploads NON monté pour nginx")

        # Vérifier env_file
        if "env_file: .env" in content:
            print_ok("  - Fichier .env chargé dans les conteneurs")
        else:
            print_warning("  - .env pourrait ne pas être chargé")

    # Dockerfile
    dockerfile = Path("Dockerfile")
    if dockerfile.exists():
        print_ok("Dockerfile trouvé")
        with open(dockerfile) as f:
            content = f.read()

        if "mkdir -p /app/static/uploads" in content:
            print_ok("  - Crée le dossier /app/static/uploads")

        if "chmod" in content and "uploads" in content:
            print_ok("  - Configure les permissions du dossier uploads")


def analyse_probleme():
    """Analyse les causes probables du problème"""
    print_section("6. ANALYSE DES CAUSES PROBABLES")

    print(f"{YELLOW}┌─────────────────────────────────────────────────────────────────┐{NC}")
    print(f"{YELLOW}│ CAUSES PROBABLES PAR ORDRE DE PROBABILITÉ                       │{NC}")
    print(f"{YELLOW}└─────────────────────────────────────────────────────────────────┘{NC}\n")

    print(f"{CYAN}1. LOG_LEVEL = 'WARNING' en production (80% probable){NC}")
    print("   → Conséquence: Les logs [FETCH_PHOTOS] (logger.info) ne s'affichent pas")
    print("   → Solution: Changer LOG_LEVEL à 'INFO' dans app/configprod.py ligne 93\n")

    print(f"{CYAN}2. Restrictions de la clé API Google Maps (70% probable){NC}")
    print("   → Conséquence: L'API refuse les requêtes depuis planflan.fr")
    print("   → Solution: Vérifier dans Google Cloud Console:")
    print("     • https://console.cloud.google.com/apis/credentials")
    print("     • Retirer temporairement les restrictions")
    print("     • Ou ajouter planflan.fr dans les référents autorisés\n")

    print(f"{CYAN}3. Pare-feu bloquant les requêtes sortantes (30% probable){NC}")
    print("   → Conséquence: Le conteneur ne peut pas contacter maps.googleapis.com")
    print("   → Solution: Autoriser les connexions sortantes vers *.googleapis.com\n")

    print(f"{CYAN}4. Variable d'environnement non chargée (20% probable){NC}")
    print("   → Conséquence: GOOGLE_MAPS_API_KEY est vide dans le conteneur")
    print("   → Solution: Vérifier que .env est au bon endroit et rebuild l'image\n")


def recommandations():
    """Affiche les recommandations"""
    print_section("7. PLAN D'ACTION RECOMMANDÉ")

    print(f"{GREEN}Étape 1: Activer les logs détaillés{NC}")
    print("  1. Éditer app/configprod.py")
    print("  2. Ligne 93: Changer LOG_LEVEL = 'INFO'")
    print("  3. docker compose restart planflan-backend")
    print()

    print(f"{GREEN}Étape 2: Vérifier la clé API Google{NC}")
    print("  1. Aller sur https://console.cloud.google.com/apis/credentials")
    print("  2. Cliquer sur votre clé API")
    print("  3. Dans 'API restrictions': vérifier que Places API est incluse")
    print("  4. Dans 'Application restrictions': retirer temporairement les restrictions")
    print()

    print(f"{GREEN}Étape 3: Tester en production{NC}")
    print("  1. Ajouter un établissement via l'interface web")
    print("  2. Immédiatement après, consulter les logs:")
    print("     docker logs planflan-container-backend 2>&1 | grep FETCH_PHOTOS | tail -50")
    print()

    print(f"{GREEN}Étape 4: Analyser les logs{NC}")
    print("  Si vous voyez:")
    print("    • 'Aucune photo trouvée' → Problème de clé API")
    print("    • 'Erreur API Google: status=403' → Restrictions de la clé")
    print("    • 'Erreur API Google: status=400' → photo_reference invalide")
    print("    • Rien → LOG_LEVEL trop élevé ou fonction non appelée")
    print()


def main():
    print(f"{BLUE}╔════════════════════════════════════════════════════════════════╗{NC}")
    print(f"{BLUE}║  ANALYSE DES DIFFÉRENCES LOCAL vs PRODUCTION                  ║{NC}")
    print(f"{BLUE}║  Photos Google Places                                          ║{NC}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════════╝{NC}")

    # Vérifier qu'on est dans le bon dossier
    if not Path("app").exists():
        print_error("Ce script doit être exécuté depuis la racine du projet planflan2")
        sys.exit(1)

    check_env_file()
    check_config_files()
    check_outils_py()
    check_routes_maps()
    check_docker_config()
    analyse_probleme()
    recommandations()

    print(f"\n{GREEN}╔════════════════════════════════════════════════════════════════╗{NC}")
    print(f"{GREEN}║  ANALYSE TERMINÉE                                              ║{NC}")
    print(f"{GREEN}╚════════════════════════════════════════════════════════════════╝{NC}\n")


if __name__ == "__main__":
    main()

"""
Module pour la gestion des en-têtes de sécurité HTTP.

Ce module ajoute des en-têtes de sécurité essentiels à toutes les réponses HTTP
pour protéger l'application contre diverses attaques web.
"""

import secrets
from flask import request, current_app, g


def add_security_headers(response):
    """
    Ajoute des en-têtes de sécurité HTTP à la réponse.

    Cette fonction est conçue pour être utilisée comme un middleware Flask
    via le décorateur @app.after_request.

    Args:
        response: L'objet réponse Flask à modifier

    Returns:
        response: L'objet réponse avec les en-têtes de sécurité ajoutés
    """
    # 1. Content Security Policy (CSP) - Protection contre XSS
    # Configuration CSP pour Flask avec Google Maps, Leaflet et ressources locales
    # Utilisation de nonces pour les scripts inline au lieu de 'unsafe-inline'
    csp_nonce = g.get("csp_nonce", "")
    # Format correct pour le nonce dans CSP : 'nonce-{valeur}' avec guillemets simples
    # Le nonce devrait toujours être disponible car généré dans before_request
    if csp_nonce:
        nonce_directive = f"'nonce-{csp_nonce}'"
        # Google Maps nécessite 'unsafe-eval' pour fonctionner correctement
        script_src = f"script-src 'self' {nonce_directive} 'unsafe-eval' "
    else:
        # Si pas de nonce (ne devrait pas arriver), ne pas autoriser les scripts inline
        nonce_directive = ""
        script_src = "script-src 'self' 'unsafe-eval' "

    csp = (
        "default-src 'self' http://localhost; "
        f"{script_src}"
        "https://maps.googleapis.com https://*.googleapis.com "
        "https://www.googletagmanager.com "
        "cdn.jsdelivr.net unpkg.com http://localhost; "
        "style-src 'self' 'unsafe-inline' "  # 'unsafe-inline' nécessaire pour les styles inline de Bootstrap/Leaflet/Google Maps
        "https://fonts.googleapis.com https://*.googleapis.com "
        "cdn.jsdelivr.net unpkg.com "
        "http://localhost; "
        "img-src 'self' data: blob: http://localhost "
        "https://maps.googleapis.com https://*.googleapis.com "
        "https://maps.gstatic.com https://*.gstatic.com "
        "cdn.jsdelivr.net unpkg.com "
        "*.tile.openstreetmap.org; "  # Wildcard pour tous les subdomains OpenStreetMap
        "font-src 'self' https://fonts.gstatic.com "
        "cdn.jsdelivr.net unpkg.com; "
        "connect-src 'self' "
        "https://maps.googleapis.com https://*.googleapis.com "
        "https://maps.gstatic.com https://*.gstatic.com "
        "https://*.google.com "  # Nécessaire pour gen_204 et autres endpoints Google
        "cdn.jsdelivr.net unpkg.com http://localhost; "
        "frame-src https://maps.googleapis.com; "
        "worker-src 'self' blob:; "  # Nécessaire pour certaines fonctionnalités de Google Maps
        "child-src 'self' blob:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self' http://localhost; "
        "frame-ancestors 'none'"
    )
    response.headers["Content-Security-Policy"] = csp

    # 2. X-Frame-Options - Protection contre le clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # 3. X-Content-Type-Options - Protection contre le MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # 4. X-XSS-Protection - Protection supplémentaire contre XSS
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # 5. Strict-Transport-Security (HSTS) - Force HTTPS
    # Note: À activer uniquement en production avec HTTPS
    if not current_app.debug and not current_app.testing:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

    # 6. Referrer-Policy - Contrôle des informations de référent
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # 7. Permissions-Policy - Contrôle des fonctionnalités du navigateur
    response.headers["Permissions-Policy"] = (
        "geolocation=(self), " "microphone=(), " "camera=(), " "payment=()"
    )

    # 8. Cache-Control pour les pages sensibles
    if request.endpoint and any(
        secure_endpoint in request.endpoint
        for secure_endpoint in ["auth.", "dashboard", "profile"]
    ):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


def init_security_headers(app):
    """
    Initialise les en-têtes de sécurité pour l'application Flask.

    Args:
        app: L'application Flask
    """

    # Générer un nonce unique pour chaque requête (pour CSP)
    @app.before_request
    def generate_csp_nonce():
        """Génère un nonce unique pour chaque requête pour le CSP."""
        g.csp_nonce = secrets.token_urlsafe(16)

    # Ajouter le middleware pour les en-têtes de sécurité
    @app.after_request
    def apply_security_headers(response):
        return add_security_headers(response)

    # Exposer le nonce aux templates
    @app.context_processor
    def inject_csp_nonce():
        """Injecte le nonce CSP dans tous les templates."""
        return {"csp_nonce": g.get("csp_nonce", "")}

    # Configurer les options de sécurité par défaut
    app.config.setdefault("SESSION_COOKIE_SECURE", True)
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("REMEMBER_COOKIE_SECURE", True)
    app.config.setdefault("REMEMBER_COOKIE_HTTPONLY", True)
    app.config.setdefault("REMEMBER_COOKIE_SAMESITE", "Lax")

    # Utiliser app.logger au lieu de current_app.logger pour éviter les problèmes de contexte
    app.logger.info("Security headers initialized")

"""Module des routes d'authentification de l'application PlanFlan.

Ce module gère toutes les fonctionnalités liées à l'authentification des utilisateurs,
y compris l'inscription, la connexion, la déconnexion et la gestion des comptes.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
from urllib.parse import urlparse, urljoin

from app import db, bcrypt
from app.models import Utilisateur
from app.forms import LoginForm, RegistrationForm
from app.outils import verifier_csrf_token

auth_bp = Blueprint("auth", __name__)


def is_safe_url(target):
    """Vérifie si une URL est interne (sécurisée pour la redirection).

    Args:
        target: L'URL à vérifier

    Returns:
        bool: True si l'URL est interne, False sinon
    """
    if not target:
        return False

    # Parser l'URL cible
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    # Vérifier que l'URL est sur le même hôte
    return test_url.scheme in ("http", "https") and test_url.netloc == ref_url.netloc


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Gère l'inscription des nouveaux utilisateurs.

    Cette route permet aux nouveaux utilisateurs de créer un compte.
    Elle valide les données du formulaire, hache le mot de passe,
    crée un nouvel utilisateur dans la base de données et le connecte automatiquement.

    Returns:
        Response: Page de création de compte (GET) ou redirection vers la page d'accueil (POST)
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hache le mot de passe directement avec bcrypt
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        new_user = Utilisateur(
            pseudo=form.pseudo.data,
            email=form.email.data,
            password=hashed_password,
            is_admin=False,
        )
        db.session.add(new_user)
        db.session.commit()

        # Connecter l'utilisateur automatiquement
        login_user(new_user)

        flash("Compte créé avec succès ! Vous êtes maintenant connecté.", "success")
        return redirect(url_for("main.index"))

    return render_template("creation_utilisateur.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Gère la connexion des utilisateurs.

    Cette route permet aux utilisateurs de se connecter à leur compte.
    Elle valide les identifiants, vérifie le mot de passe et établit une session.

    Returns:
        Response: Page de connexion (GET) ou redirection vers la page demandée (POST)
    """
    form = LoginForm()
    if request.method == "GET":
        # Remplis le champ caché 'next' avec la valeur de l'URL
        form.next.data = request.args.get("next", "")

    if form.validate_on_submit():
        user = Utilisateur.query.filter_by(pseudo=form.pseudo.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            # Redirige vers la page stockée dans 'next', ou vers une page par défaut
            next_page = form.next.data or request.args.get("next", "")

            # Valider que l'URL de redirection est interne (sécurisée)
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            else:
                return redirect(url_for("main.index"))

        flash("Pseudo ou mot de passe incorrect.", "danger")
    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Gère la déconnexion des utilisateurs.

    Cette route permet aux utilisateurs de se déconnecter de leur session.
    Elle termine la session utilisateur et redirige vers la page précédente
    ou vers la page d'accueil si aucune page précédente n'est disponible.

    Returns:
        Response: Redirection vers la page précédente ou la page d'accueil
    """
    logout_user()
    # Redirige vers la page précédente ou vers l'index si la page précédente n'est pas disponible
    return redirect(request.referrer or url_for("main.index"))


@auth_bp.route("/supprimer_compte", methods=["POST"])
@login_required
def supprimer_compte():
    """Delete the current user's account.

    This is a security-critical operation that requires password verification
    and CSRF token validation. The user must provide their password to confirm
    account deletion, which will cascade delete all associated data.

    Returns:
        Response: Redirect to dashboard on success, or back to referrer on error

    Raises:
        Unauthorized: If CSRF token is invalid or password is missing/incorrect
    """
    # Vérifier le token CSRF en utilisant la fonction utilitaire
    csrf_valide, message = verifier_csrf_token()
    if not csrf_valide:
        flash("Token CSRF invalide. Veuillez réessayer.", "danger")
        return redirect(url_for("main.dashboard"))

    # Vérifier la présence du mot de passe
    password = request.form.get("password")
    if not password:
        flash("Le mot de passe est requis pour supprimer le compte.", "danger")
        return redirect(url_for("main.dashboard"))

    # Vérifier le mot de passe
    if not bcrypt.check_password_hash(current_user.password, password):
        flash("Mot de passe incorrect.", "danger")
        return redirect(url_for("main.dashboard"))

    # Suppression du compte
    user = db.session.get(Utilisateur, current_user.id_user)
    db.session.delete(user)
    db.session.commit()
    flash("Votre compte a bien été supprimé", "success")
    return redirect(url_for("main.index"))

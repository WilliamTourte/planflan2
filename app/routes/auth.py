"""Module des routes d'authentification de l'application PlanFlan.

Ce module gère toutes les fonctionnalités liées à l'authentification des utilisateurs,
y compris l'inscription, la connexion, la déconnexion et la gestion des comptes.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash

from app import db, bcrypt
from app.models import Utilisateur
from app.forms import LoginForm, RegistrationForm
from app.outils import verifier_csrf_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Gère l'inscription des nouveaux utilisateurs.
    
    Cette route permet aux nouveaux utilisateurs de créer un compte.
    Elle valide les données du formulaire, hache le mot de passe,
    et crée un nouvel utilisateur dans la base de données.
    
    Returns:
        Response: Page de création de compte (GET) ou redirection vers la page de connexion (POST)
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hache le mot de passe directement avec bcrypt
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )

        new_user = Utilisateur(
            pseudo=form.pseudo.data,
            email=form.email.data,
            password=hashed_password,
            is_admin=False,
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Compte créé avec succès !", "success")
        return redirect(url_for("auth.login"))

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
            next_page = form.next.data or request.args.get(
                "next", url_for("main.index")
            )

            return redirect(next_page)

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
    # Vérifier le token CSRF en utilisant la fonction utilitaire
    csrf_valide, message = verifier_csrf_token()
    if not csrf_valide:
        return redirect(url_for("main.dashboard", error="csrf"))

    # Vérifier le mot de passe pour les actions sensibles
    password = request.form.get("password")
    if not password or not bcrypt.check_password_hash(current_user.password, password):
        return redirect(url_for("main.dashboard", error="password"))

    user = Utilisateur.query.get(current_user.id_user)
    db.session.delete(user)
    db.session.commit()
    flash("Votre compte a bien été supprimé", "success")
    return redirect(url_for("main.index"))

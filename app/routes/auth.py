from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash, generate_password_hash

from app import db, bcrypt
from app.models import Utilisateur
from app.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hache le mot de passe directement avec bcrypt
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        new_user = Utilisateur(
            pseudo=form.pseudo.data,
            email=form.email.data,
            password=hashed_password,
            is_admin=False,
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Compte créé avec succès !', 'success')
        return redirect(url_for('auth.login'))

    return render_template('creation_utilisateur.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        # Remplis le champ caché 'next' avec la valeur de l'URL
        form.next.data = request.args.get('next', '')

    if form.validate_on_submit():
        user = Utilisateur.query.filter_by(pseudo=form.pseudo.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            # Redirige vers la page stockée dans 'next', ou vers une page par défaut
            next_page = form.next.data or request.args.get('next', url_for('main.index'))

            return redirect(next_page)

        flash('Pseudo ou mot de passe incorrect.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    # Redirige vers la page précédente ou vers l'index si la page précédente n'est pas disponible
    return redirect(request.referrer or url_for('main.index'))

@auth_bp.route('/supprimer_compte', methods=['POST'])
@login_required
def supprimer_compte():
    user = Utilisateur.query.get(current_user.id_user)
    db.session.delete(user)
    db.session.commit()
    flash('Votre compte a bien été supprimé', 'success')
    return redirect(url_for('main.index'))

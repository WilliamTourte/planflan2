from app import create_app, db, bcrypt
from app.models import Utilisateur, Etablissement, Flan

# Crée l'application
app = create_app()

with app.app_context():
    # Trouve ou crée un utilisateur admin
    admin = Utilisateur.query.filter_by(is_admin=True).first()
    if not admin:
        print("Création de l'utilisateur admin par défaut...")
        admin = Utilisateur(
            pseudo="Admin",
            email="admin@planflan.fr",
            is_admin=True
        )
        admin.set_password("Admin123!", bcrypt)  # Remplace par un mot de passe sécurisé
        db.session.add(admin)
        db.session.commit()
        print(f"Admin créé avec ID : {admin.id_user}")

    # Mets à jour les établissements sans id_user
    result_etab = Etablissement.query.filter_by(id_user=None).update({"id_user": admin.id_user})
    print(f"{result_etab} établissements mis à jour.")

    # Mets à jour les flans sans id_user
    result_flan = Flan.query.filter_by(id_user=None).update({"id_user": admin.id_user})
    print(f"{result_flan} flans mis à jour.")

    db.session.commit()
    print("Mise à jour terminée !")

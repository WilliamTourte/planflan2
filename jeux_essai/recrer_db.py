from app import create_app, db, bcrypt

# Crée l'instance de l'application
app = create_app()

# Crée le contexte d'application
with app.app_context():


    # Crée toutes les tables
    db.create_all()

    # Importe les modèles après la création de l'app
    from app.models import Utilisateur, TypeEtab, Etablissement, Flan, Evaluation, Photo, StatutEval, TypeCible

    # Exemple : Création d'un utilisateur admin
    admin = Utilisateur(
        pseudo="admin",
        email="admin@example.com",
        is_admin=True
    )
    admin.set_password("adminpassword", bcrypt)
    db.session.add(admin)

    # Exemple : Création d'un établissement et d'un flan
    etab = Etablissement(
        type_etab=TypeEtab.BOULANGERIE,
        nom="Boulangerie Test",
        adresse="123 Rue de Test",
        code_postal="75000",
        ville="Paris",
        label=True
    )
    db.session.add(etab)

    flan = Flan(
        nom="Flan Nature",
        description="Un délicieux flan nature.",
        prix=3.50,
        etablissement=etab
    )
    db.session.add(flan)

    # Valide les changements
    db.session.commit()

    print("✅ Tables recréées avec succès !")
    print("📋 Tables disponibles :")
    for table_name in db.metadata.tables.keys():
        print(f"  - {table_name}")

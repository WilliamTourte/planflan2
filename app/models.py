from app import db, login_manager, bcrypt
from flask_login import UserMixin

class Utilisateur(db.Model, UserMixin):
    __tablename__ = 'utilisateurs'
    id_user = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False) # par défaut un utilisateur n'est pas administrateur'

    def get_id(self): # Pour que get_id de Flask Login utilise l'id_user' plutôt que 'id' par défaut
        return str(self.id_user)

    def set_password(self, password): # Hache le mot de passe
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password): # Vérifie que le mot de passe est correct
        return bcrypt.check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id): # Prend un user_id pour charger un utilisateur
    return Utilisateur.query.get(int(user_id))

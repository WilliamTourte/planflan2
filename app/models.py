from app import db, login_manager, bcrypt
from flask_login import UserMixin

class Utilisateur(db.Model, UserMixin):
    __tablename__ = 'utilisateurs'
    id_user = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    return Utilisateur.query.get(int(user_id))

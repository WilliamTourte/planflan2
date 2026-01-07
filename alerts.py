import logging
from logging.handlers import SMTPHandler

def setup_alerts():
    """Configure les alertes par email pour les opérations critiques."""
    # Configuration du logging pour les alertes
    alert_logger = logging.getLogger('alerts')
    alert_logger.setLevel(logging.WARNING)
    
    # Configuration de l'envoi d'emails
    mail_handler = SMTPHandler(
        mailhost=('smtp.example.com', 587),
        fromaddr='alerts@example.com',
        toaddrs=['admin@example.com'],
        subject='ALERTE : Operation critique sur la base de donnees',
        credentials=('username', 'password'),
        secure=()
    )
    mail_handler.setLevel(logging.WARNING)
    
    # Format des alertes
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    mail_handler.setFormatter(formatter)
    
    # Ajouter le handler au logger
    alert_logger.addHandler(mail_handler)
    
    return alert_logger

# Exemple d'utilisation
def log_critical_operation(message):
    """Log une operation critique et envoie une alerte."""
    alert_logger = setup_alerts()
    alert_logger.warning(message)

if __name__ == "__main__":
    log_critical_operation("Test d'alerte : Operation critique detectee")
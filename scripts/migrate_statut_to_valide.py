#!/usr/bin/env python3
"""
Script de migration pour mettre à jour les statuts EN_ATTENTE vers VALIDE.

Ce script met à jour tous les enregistrements dans la base de données qui ont
le statut "EN_ATTENTE" pour les passer à "VALIDE", conformément à la nouvelle
stratégie de modération a posteriori.
"""

import sys
import os

# Ajouter le chemin du projet au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Etablissement, Flan, Evaluation

def migrate_statuts():
    """Mettre à jour tous les statuts EN_ATTENTE vers VALIDE."""
    print("Début de la migration des statuts...")
    
    try:
        # Créer l'application Flask
        app = create_app()
        
        with app.app_context():
            print("Connexion à la base de données...")
            
            # Compter les enregistrements avant migration
            etab_en_attente = Etablissement.query.filter_by(statut='EN_ATTENTE').count()
            flan_en_attente = Flan.query.filter_by(statut='EN_ATTENTE').count()
            eval_en_attente = Evaluation.query.filter_by(statut='EN_ATTENTE').count()
            
            print(f"Établissements en attente: {etab_en_attente}")
            print(f"Flans en attente: {flan_en_attente}")
            print(f"Évaluations en attente: {eval_en_attente}")
            
            if etab_en_attente == 0 and flan_en_attente == 0 and eval_en_attente == 0:
                print("Aucun enregistrement à migrer. La migration n'est pas nécessaire.")
                return True
            
            # Mettre à jour les établissements
            if etab_en_attente > 0:
                print(f"Migration de {etab_en_attente} établissements...")
                db.session.query(Etablissement).filter_by(statut='EN_ATTENTE').update({'statut': 'VALIDE'})
                print("Établissements migrés avec succès.")
            
            # Mettre à jour les flans
            if flan_en_attente > 0:
                print(f"Migration de {flan_en_attente} flans...")
                db.session.query(Flan).filter_by(statut='EN_ATTENTE').update({'statut': 'VALIDE'})
                print("Flans migrés avec succès.")
            
            # Mettre à jour les évaluations
            if eval_en_attente > 0:
                print(f"Migration de {eval_en_attente} évaluations...")
                db.session.query(Evaluation).filter_by(statut='EN_ATTENTE').update({'statut': 'VALIDE'})
                print("Évaluations migrées avec succès.")
            
            # Valider les changements
            db.session.commit()
            print("Migration terminée avec succès!")
            
            # Vérification post-migration
            etab_restants = Etablissement.query.filter_by(statut='EN_ATTENTE').count()
            flan_restants = Flan.query.filter_by(statut='EN_ATTENTE').count()
            eval_restants = Evaluation.query.filter_by(statut='EN_ATTENTE').count()
            
            print(f"Vérification post-migration:")
            print(f"Établissements encore en attente: {etab_restants}")
            print(f"Flans encore en attente: {flan_restants}")
            print(f"Évaluations encore en attente: {eval_restants}")
            
            return True
            
    except Exception as e:
        print(f"Erreur lors de la migration: {str(e)}")
        db.session.rollback()
        return False

def main():
    """Fonction principale."""
    print("Script de migration des statuts EN_ATTENTE vers VALIDE")
    print("=" * 60)
    
    # Demander confirmation
    response = input("Cette opération mettra à jour tous les statuts EN_ATTENTE vers VALIDE.\n"
                     "Voulez-vous continuer? (o/n): ")
    
    if response.lower() != 'o':
        print("Migration annulée.")
        sys.exit(0)
    
    # Exécuter la migration
    success = migrate_statuts()
    
    if success:
        print("\nMigration terminée avec succès!")
        sys.exit(0)
    else:
        print("\nLa migration a échoué.")
        sys.exit(1)

if __name__ == "__main__":
    main()
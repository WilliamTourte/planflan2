"""Migration to fix EN_ATTENTE issue

Revision ID: fix_en_attente
Revises: fd3cb8773fda
Create Date: 2026-02-13 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "fix_en_attente"
down_revision = "fd3cb8773fda"
branch_labels = None
depends_on = None


def upgrade():
    # Change default value from EN_ATTENTE to VALIDE
    op.execute("ALTER TABLE etablissements ALTER COLUMN statut SET DEFAULT 'VALIDE'")
    op.execute("ALTER TABLE flans ALTER COLUMN statut SET DEFAULT 'VALIDE'")
    op.execute("ALTER TABLE evaluations ALTER COLUMN statut SET DEFAULT 'VALIDE'")

    # Update existing records with EN_ATTENTE status
    op.execute("UPDATE etablissements SET statut = 'VALIDE' WHERE statut = 'EN_ATTENTE'")
    op.execute("UPDATE flans SET statut = 'VALIDE' WHERE statut = 'EN_ATTENTE'")
    op.execute("UPDATE evaluations SET statut = 'VALIDE' WHERE statut = 'EN_ATTENTE'")

    # Modify the Enum type to remove EN_ATTENTE
    # This is MySQL-specific and requires careful handling
    op.execute("""
        ALTER TABLE etablissements
        MODIFY COLUMN statut ENUM('VALIDE', 'SUPPRIME') NOT NULL DEFAULT 'VALIDE'
    """)
    op.execute("""
        ALTER TABLE flans
        MODIFY COLUMN statut ENUM('VALIDE', 'SUPPRIME') NOT NULL DEFAULT 'VALIDE'
    """)
    op.execute("""
        ALTER TABLE evaluations
        MODIFY COLUMN statut ENUM('VALIDE', 'SUPPRIME') NOT NULL DEFAULT 'VALIDE'
    """)


def downgrade():
    # Revert changes (add EN_ATTENTE back)
    op.execute("""
        ALTER TABLE etablissements
        MODIFY COLUMN statut ENUM('EN_ATTENTE', 'VALIDE', 'SUPPRIME') NOT NULL DEFAULT 'EN_ATTENTE'
    """)
    op.execute("""
        ALTER TABLE flans
        MODIFY COLUMN statut ENUM('EN_ATTENTE', 'VALIDE', 'SUPPRIME') NOT NULL DEFAULT 'EN_ATTENTE'
    """)
    op.execute("""
        ALTER TABLE evaluations
        MODIFY COLUMN statut ENUM('EN_ATTENTE', 'VALIDE', 'SUPPRIME') NOT NULL DEFAULT 'EN_ATTENTE'
    """)

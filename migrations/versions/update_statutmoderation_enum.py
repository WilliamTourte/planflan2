"""Update StatutModeration enum to remove EN_ATTENTE

Revision ID: update_statutmoderation_enum
Revises: 822e8c700aa1
Create Date: 2024-01-15 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "update_statutmoderation_enum"
down_revision = "822e8c700aa1"
branch_labels = None
depends_on = None


def upgrade():
    # For PostgreSQL, we need to recreate the enum type
    # First, drop the constraints that depend on the enum
    with op.batch_alter_table("etablissements", schema=None) as batch_op:
        batch_op.alter_column(
            "statut",
            existing_type=sa.Enum("EN_ATTENTE", "VALIDE", "SUPPRIME", name="statutmoderation"),
            type_=sa.Enum("VALIDE", "SUPPRIME", name="statutmoderation"),
            existing_nullable=False,
        )

    with op.batch_alter_table("flans", schema=None) as batch_op:
        batch_op.alter_column(
            "statut",
            existing_type=sa.Enum("EN_ATTENTE", "VALIDE", "SUPPRIME", name="statutmoderation"),
            type_=sa.Enum("VALIDE", "SUPPRIME", name="statutmoderation"),
            existing_nullable=False,
        )

    with op.batch_alter_table("evaluations", schema=None) as batch_op:
        batch_op.alter_column(
            "statut",
            existing_type=sa.Enum("EN_ATTENTE", "VALIDE", "SUPPRIME", name="statutmoderation"),
            type_=sa.Enum("VALIDE", "SUPPRIME", name="statutmoderation"),
            existing_nullable=False,
        )


def downgrade():
    # Revert to the old enum type
    with op.batch_alter_table("evaluations", schema=None) as batch_op:
        batch_op.alter_column(
            "statut",
            existing_type=sa.Enum("VALIDE", "SUPPRIME", name="statutmoderation"),
            type_=sa.Enum("EN_ATTENTE", "VALIDE", "SUPPRIME", name="statutmoderation"),
            existing_nullable=False,
        )

    with op.batch_alter_table("flans", schema=None) as batch_op:
        batch_op.alter_column(
            "statut",
            existing_type=sa.Enum("VALIDE", "SUPPRIME", name="statutmoderation"),
            type_=sa.Enum("EN_ATTENTE", "VALIDE", "SUPPRIME", name="statutmoderation"),
            existing_nullable=False,
        )

    with op.batch_alter_table("etablissements", schema=None) as batch_op:
        batch_op.alter_column(
            "statut",
            existing_type=sa.Enum("VALIDE", "SUPPRIME", name="statutmoderation"),
            type_=sa.Enum("EN_ATTENTE", "VALIDE", "SUPPRIME", name="statutmoderation"),
            existing_nullable=False,
        )
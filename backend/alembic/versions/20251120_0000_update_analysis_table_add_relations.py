"""update analysis table add relations

Revision ID: update_analysis_relations
Revises: 5c1612cd246b
Create Date: 2025-11-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'update_analysis_relations'
down_revision: Union[str, Sequence[str], None] = '5c1612cd246b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Crear nueva tabla con estructura corregida
    op.create_table('analysis_new',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('total_lines', sa.Integer(), nullable=False),
        sa.Column('code_lines', sa.Integer(), nullable=False),
        sa.Column('complexity', sa.Integer(), nullable=False),
        sa.Column('num_functions', sa.Integer(), nullable=False),
        sa.Column('num_classes', sa.Integer(), nullable=False),
        sa.Column('num_imports', sa.Integer(), nullable=False),
        sa.Column('functions_data', sa.JSON(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear índices
    op.create_index(op.f('ix_analysis_new_project_id'), 'analysis_new', ['project_id'], unique=False)
    op.create_index(op.f('ix_analysis_new_user_id'), 'analysis_new', ['user_id'], unique=False)

    # Eliminar tabla antigua (si existe y tiene datos, migrarlos antes)
    op.drop_table('analysis')

    # Renombrar nueva tabla
    op.rename_table('analysis_new', 'analysis')

    # Renombrar índices
    op.execute("ALTER INDEX ix_analysis_new_project_id RENAME TO ix_analysis_project_id")
    op.execute("ALTER INDEX ix_analysis_new_user_id RENAME TO ix_analysis_user_id")


def downgrade() -> None:
    """Downgrade schema."""
    # Crear tabla antigua
    op.create_table('analysis_old',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('total_lines', sa.Integer(), nullable=False),
        sa.Column('code_lines', sa.Integer(), nullable=False),
        sa.Column('complexity', sa.Integer(), nullable=False),
        sa.Column('num_functions', sa.Integer(), nullable=False),
        sa.Column('num_classes', sa.Integer(), nullable=False),
        sa.Column('num_imports', sa.Integer(), nullable=False),
        sa.Column('functions_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Eliminar tabla nueva
    op.drop_index(op.f('ix_analysis_user_id'), table_name='analysis')
    op.drop_index(op.f('ix_analysis_project_id'), table_name='analysis')
    op.drop_table('analysis')

    # Renombrar tabla antigua
    op.rename_table('analysis_old', 'analysis')

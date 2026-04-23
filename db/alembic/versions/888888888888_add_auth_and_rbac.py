"""add auth and RBAC

Revision ID: 888888888888
Revises: 777777777777
Create Date: 2026-04-23 23:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '888888888888'
down_revision = '777777777777'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add auth fields to users
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    op.add_column('users', sa.Column('role', sa.String(), server_default='viewer', nullable=False))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    
    # 2. Add unique constraint to email
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    
    # 3. Create user_plants mapping table
    op.create_table(
        'user_plants',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('plant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('plants.id', ondelete='CASCADE'), primary_key=True)
    )
    
    # Set existing users to have a dummy password (in production this would be handled differently)
    op.execute("UPDATE users SET hashed_password = 'placeholder_hash' WHERE hashed_password IS NULL")
    op.alter_column('users', 'hashed_password', nullable=False)


def downgrade():
    op.drop_table('user_plants')
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'role')
    op.drop_column('users', 'hashed_password')

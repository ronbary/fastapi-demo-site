"""create user_votes table

Revision ID: 97b4d644615a
Revises: b36affb12225
Create Date: 2022-06-10 00:25:16.413764

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97b4d644615a'
down_revision = 'b36affb12225'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user_votes',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts2.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'post_id')
    )
    pass


def downgrade():
    op.drop_table('user_votes')
    pass

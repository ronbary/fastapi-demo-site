"""create posts2 table

Revision ID: 61e265c521e7
Revises: 
Create Date: 2022-06-10 00:17:44.747419

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '61e265c521e7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('posts2',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('content', sa.String(), nullable=False),
                    sa.Column('published', sa.Boolean(), nullable=False, server_default='TRUE'),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                              server_default=sa.text('NOW()')),
                    sa.Column('owner_id', sa.Integer(), nullable=False),
                    )
    op.create_foreign_key('post_users_fk', source_table="posts2", referent_table="users",
                          local_cols=[
                              'owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade():
    op.drop_table('posts2')
    pass

"""empty message

Revision ID: d15a3548829e
Revises: 
Create Date: 2018-11-11 09:47:04.843084

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd15a3548829e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('radius', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'))
    op.create_table(
        'prom_codes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('credit', sa.Float(), nullable=True),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('radius', sa.Float(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('creation_time', sa.DateTime(), nullable=False),
        sa.Column('expiration_time', sa.DateTime(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['event_id'],
            ['events.id'],
        ), sa.PrimaryKeyConstraint('id', 'code'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prom_codes')
    op.drop_table('events')
    # ### end Alembic commands ###

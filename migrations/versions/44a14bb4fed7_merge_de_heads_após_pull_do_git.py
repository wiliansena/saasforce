"""merge de heads após pull do git

Revision ID: 44a14bb4fed7
Revises: 1418cdf1de45, beae2662492e
Create Date: 2025-12-29 01:53:42.330219

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44a14bb4fed7'
down_revision = ('1418cdf1de45', 'beae2662492e')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

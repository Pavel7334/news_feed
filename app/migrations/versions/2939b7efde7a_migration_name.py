"""migration name

Revision ID: 2939b7efde7a
Revises: 0a1c7d39ea3f
Create Date: 2024-03-14 20:45:39.728194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2939b7efde7a'
down_revision: Union[str, None] = '0a1c7d39ea3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('news', sa.Column('slug', sa.String(), server_default='', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('news', 'slug')
    # ### end Alembic commands ###

"""migration name

Revision ID: 5ee3bf9e1f74
Revises: 2939b7efde7a
Create Date: 2024-03-14 22:39:22.511211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ee3bf9e1f74'
down_revision: Union[str, None] = '2939b7efde7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'news', ['slug'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'news', type_='unique')
    # ### end Alembic commands ###
"""deleted the field rating from the model News

Revision ID: 99bdbcba4a0c
Revises: f8d2561ffcf9
Create Date: 2024-03-06 15:58:50.462880

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99bdbcba4a0c'
down_revision: Union[str, None] = 'f8d2561ffcf9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('news', 'rating')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('news', sa.Column('rating', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
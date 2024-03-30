"""remove source_description field from artworks

Revision ID: a43d9a90123d
Revises: 10c682ac3701
Create Date: 2024-01-14 16:47:50.844231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a43d9a90123d"
down_revision: Union[str, None] = "10c682ac3701"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("artwork", "source_description")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "artwork",
        sa.Column(
            "source_description", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    # ### end Alembic commands ###
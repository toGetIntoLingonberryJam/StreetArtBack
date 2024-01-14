"""Artist and festival image

Revision ID: cac492ca403b
Revises: a43d9a90123d
Create Date: 2024-01-14 19:24:33.462075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cac492ca403b"
down_revision: Union[str, None] = "a43d9a90123d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("artist", sa.Column("image_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "artist", "image", ["image_id"], ["id"])
    op.add_column("festival", sa.Column("image_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "festival", "image", ["image_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "festival", type_="foreignkey")
    op.drop_column("festival", "image_id")
    op.drop_constraint(None, "artist", type_="foreignkey")
    op.drop_column("artist", "image_id")
    # ### end Alembic commands ###

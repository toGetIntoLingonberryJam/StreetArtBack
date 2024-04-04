"""Updating ArtworkImage

Revision ID: 84cfe4e02e2a
Revises: ffe148f9cede
Create Date: 2023-11-17 12:42:32.882727

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "84cfe4e02e2a"
down_revision: Union[str, None] = "ffe148f9cede"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "artwork_images", ["image_url"])
    op.drop_column("artwork_images", "thumbnail_url")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "artwork_images",
        sa.Column("thumbnail_url", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(None, "artwork_images", type_="unique")
    # ### end Alembic commands ###

"""Artwork reactions update

Revision ID: 8dc94edf8de1
Revises: 1546ee27c97f
Create Date: 2024-01-04 20:53:15.445658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8dc94edf8de1"
down_revision: Union[str, None] = "1546ee27c97f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "reaction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("artworks_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["artworks_id"],
            ["artworks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("reaction")
    # ### end Alembic commands ###
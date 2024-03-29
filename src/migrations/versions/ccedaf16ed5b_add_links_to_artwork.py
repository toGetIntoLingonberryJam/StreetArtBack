"""add links to artwork

Revision ID: ccedaf16ed5b
Revises: e7c6ee8025f3
Create Date: 2024-01-13 21:49:49.924774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ccedaf16ed5b"
down_revision: Union[str, None] = "e7c6ee8025f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "artist", "links", existing_type=postgresql.ARRAY(sa.VARCHAR()), nullable=True
    )
    op.add_column("artwork", sa.Column("links", sa.ARRAY(sa.String()), nullable=True))
    op.alter_column("artwork", "description", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column(
        "artwork", "source_description", existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        "festival", "links", existing_type=postgresql.ARRAY(sa.VARCHAR()), nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "festival",
        "links",
        existing_type=postgresql.ARRAY(sa.VARCHAR()),
        nullable=False,
    )
    op.alter_column(
        "artwork", "source_description", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "artwork", "description", existing_type=sa.VARCHAR(), nullable=False
    )
    op.drop_column("artwork", "links")
    op.alter_column(
        "artist", "links", existing_type=postgresql.ARRAY(sa.VARCHAR()), nullable=False
    )
    # ### end Alembic commands ###

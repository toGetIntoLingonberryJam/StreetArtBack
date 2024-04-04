"""Added ArtworkModeration model

Revision ID: 84b3accab5b5
Revises: 9603dfa7c9fd
Create Date: 2023-11-08 18:56:33.746720

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "84b3accab5b5"
down_revision: Union[str, None] = "9603dfa7c9fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "artwork_moderation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("artwork_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", name="artworkmoderationstatus"),
            nullable=True,
        ),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["artwork_id"],
            ["artworks.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("artwork_id"),
    )
    op.create_index(
        op.f("ix_artwork_moderation_id"), "artwork_moderation", ["id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_artwork_moderation_id"), table_name="artwork_moderation")
    op.drop_table("artwork_moderation")
    # ### end Alembic commands ###

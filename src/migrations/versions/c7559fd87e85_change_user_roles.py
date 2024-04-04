"""Change user roles

Revision ID: c7559fd87e85
Revises: 84cfe4e02e2a
Create Date: 2023-11-18 22:48:24.623299

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7559fd87e85"
down_revision: Union[str, None] = "84cfe4e02e2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "artist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_artist_user_id"), "artist", ["user_id"], unique=False)
    op.create_table(
        "moderator",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_moderator_user_id"), "moderator", ["user_id"], unique=False
    )
    op.add_column(
        "user",
        sa.Column(
            "is_artist", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "is_moderator",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "is_moderator")
    op.drop_column("user", "is_artist")
    op.drop_index(op.f("ix_moderator_user_id"), table_name="moderator")
    op.drop_table("moderator")
    op.drop_index(op.f("ix_artist_user_id"), table_name="artist")
    op.drop_table("artist")
    # ### end Alembic commands ###

"""Added Tickets models

Revision ID: cca3346b3585
Revises: 23cb7ad28b4a
Create Date: 2023-12-30 10:36:08.094067

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cca3346b3585"
down_revision: Union[str, None] = "23cb7ad28b4a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "ticket_type",
            sa.Enum("CREATE", "EDIT", "COMPLAIN", name="tickettype"),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "ACCEPTED", "REJECTED", name="ticketstatus"),
            nullable=True,
        ),
        sa.Column("moderator_comment", sa.Text(), nullable=True),
        sa.Column("discriminator", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("artwork_id", sa.Integer(), nullable=True),
        sa.Column("artwork_data", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["artwork_id"],
            ["artworks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tickets_artwork_id"), "tickets", ["artwork_id"], unique=False
    )
    op.create_index(op.f("ix_tickets_id"), "tickets", ["id"], unique=False)
    op.create_index(op.f("ix_tickets_user_id"), "tickets", ["user_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_tickets_user_id"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_id"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_artwork_id"), table_name="tickets")
    op.drop_table("tickets")
    # ### end Alembic commands ###

"""Image Description + Ticket Moderator

Revision ID: a2539b46e267
Revises: ccedaf16ed5b
Create Date: 2024-01-14 11:52:18.698800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a2539b46e267"
down_revision: Union[str, None] = "ccedaf16ed5b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "image", sa.Column("description", sa.String(length=50), nullable=True)
    )
    op.add_column("ticket", sa.Column("moderator_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "ticket", "moderator", ["moderator_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "ticket", type_="foreignkey")
    op.drop_column("ticket", "moderator_id")
    op.drop_column("image", "description")
    # ### end Alembic commands ###

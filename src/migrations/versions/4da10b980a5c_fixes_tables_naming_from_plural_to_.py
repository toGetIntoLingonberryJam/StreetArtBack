"""Fixes tables naming: from plural to singular + fix ticket model

Revision ID: 4da10b980a5c
Revises: cca3346b3585
Create Date: 2023-12-31 17:59:55.937133

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4da10b980a5c"
down_revision: Union[str, None] = "cca3346b3585"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Rename the table
    op.rename_table("artworks", "artwork")
    op.rename_table("artwork_images", "artwork_image")
    op.rename_table("tickets", "ticket")

    # Rename the index
    op.execute("ALTER INDEX ix_artworks_id RENAME TO ix_artwork_id")
    op.execute("ALTER INDEX ix_artworks_title RENAME TO ix_artwork_title")
    op.execute("ALTER INDEX ix_artwork_images_id RENAME TO ix_artwork_image_id")
    op.execute("ALTER INDEX ix_tickets_artwork_id RENAME TO ix_ticket_artwork_id")
    op.execute("ALTER INDEX ix_tickets_id RENAME TO ix_ticket_id")
    op.execute("ALTER INDEX ix_tickets_user_id RENAME TO ix_ticket_user_id")

    # Modify ticket table
    op.alter_column(
        "ticket", "discriminator", existing_type=sa.VARCHAR(), nullable=False
    )


def downgrade():
    # Rename back to the original table name
    op.rename_table("artwork", "artworks")
    op.rename_table("artwork_image", "artwork_images")
    op.rename_table("ticket", "tickets")

    # Rename back the index
    op.execute("ALTER INDEX ix_artwork_id RENAME TO ix_artworks_id")
    op.execute("ALTER INDEX ix_artwork_title RENAME TO ix_artworks_title")
    op.execute("ALTER INDEX ix_artwork_image_id RENAME TO ix_artwork_images_id")
    op.execute("ALTER INDEX ix_ticket_artwork_id RENAME TO ix_tickets_artwork_id")
    op.execute("ALTER INDEX ix_ticket_id RENAME TO ix_tickets_id")
    op.execute("ALTER INDEX ix_ticket_user_id RENAME TO ix_tickets_user_id")

    # Modify back ticket table
    op.alter_column(
        "tickets", "discriminator", existing_type=sa.VARCHAR(), nullable=True
    )

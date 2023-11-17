"""fix artwork relationship

Revision ID: ffe148f9cede
Revises: 84b3accab5b5
Create Date: 2023-11-12 04:38:58.322493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffe148f9cede'
down_revision: Union[str, None] = '84b3accab5b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('artwork_additions_artwork_id_fkey', 'artwork_additions', type_='foreignkey')
    op.create_foreign_key(None, 'artwork_additions', 'artworks', ['artwork_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('artwork_images_artwork_id_fkey', 'artwork_images', type_='foreignkey')
    op.create_foreign_key(None, 'artwork_images', 'artworks', ['artwork_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('artwork_location_artwork_id_fkey', 'artwork_location', type_='foreignkey')
    op.create_foreign_key(None, 'artwork_location', 'artworks', ['artwork_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('artwork_moderation_artwork_id_fkey', 'artwork_moderation', type_='foreignkey')
    op.create_foreign_key(None, 'artwork_moderation', 'artworks', ['artwork_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'artwork_moderation', type_='foreignkey')
    op.create_foreign_key('artwork_moderation_artwork_id_fkey', 'artwork_moderation', 'artworks', ['artwork_id'], ['id'])
    op.drop_constraint(None, 'artwork_location', type_='foreignkey')
    op.create_foreign_key('artwork_location_artwork_id_fkey', 'artwork_location', 'artworks', ['artwork_id'], ['id'])
    op.drop_constraint(None, 'artwork_images', type_='foreignkey')
    op.create_foreign_key('artwork_images_artwork_id_fkey', 'artwork_images', 'artworks', ['artwork_id'], ['id'])
    op.drop_constraint(None, 'artwork_additions', type_='foreignkey')
    op.create_foreign_key('artwork_additions_artwork_id_fkey', 'artwork_additions', 'artworks', ['artwork_id'], ['id'])
    # ### end Alembic commands ###
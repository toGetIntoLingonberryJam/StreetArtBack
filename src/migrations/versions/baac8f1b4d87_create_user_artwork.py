"""create User + Artwork

Revision ID: baac8f1b4d87
Revises: 
Create Date: 2023-10-31 17:33:55.097345

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'baac8f1b4d87'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('artworks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('year_created', sa.Integer(), nullable=True),
    sa.Column('festival', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('source_description', sa.String(), nullable=True),
    sa.Column('added_by_user_id', sa.Integer(), nullable=True),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('EXISTING', 'DESTROYED', 'OVERPAINTED', name='artworkstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['added_by_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['artist_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artworks_id'), 'artworks', ['id'], unique=False)
    op.create_index(op.f('ix_artworks_title'), 'artworks', ['title'], unique=False)
    op.create_table('artwork_additions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artwork_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artwork_id'], ['artworks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artwork_additions_id'), 'artwork_additions', ['id'], unique=False)
    op.create_table('artwork_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('thumbnail_url', sa.String(), nullable=True),
    sa.Column('artwork_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artwork_id'], ['artworks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artwork_images_id'), 'artwork_images', ['id'], unique=False)
    op.create_table('artwork_location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('thumbnail_image_id', sa.Integer(), nullable=True),
    sa.Column('artwork_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artwork_id'], ['artworks.id'], ),
    sa.ForeignKeyConstraint(['thumbnail_image_id'], ['artwork_images.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('artwork_id')
    )
    op.create_index(op.f('ix_artwork_location_id'), 'artwork_location', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_artwork_location_id'), table_name='artwork_location')
    op.drop_table('artwork_location')
    op.drop_index(op.f('ix_artwork_images_id'), table_name='artwork_images')
    op.drop_table('artwork_images')
    op.drop_index(op.f('ix_artwork_additions_id'), table_name='artwork_additions')
    op.drop_table('artwork_additions')
    op.drop_index(op.f('ix_artworks_title'), table_name='artworks')
    op.drop_index(op.f('ix_artworks_id'), table_name='artworks')
    op.drop_table('artworks')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###

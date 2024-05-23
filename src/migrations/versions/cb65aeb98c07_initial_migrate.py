"""initial migrate

Revision ID: cb65aeb98c07
Revises: 
Create Date: 2024-05-21 22:47:48.988173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cb65aeb98c07'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('public_key', sa.String(), nullable=False),
    sa.Column('file_path', sa.String(), nullable=False),
    sa.Column('description', sa.String(length=50), nullable=True),
    sa.Column('discriminator', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_id'), 'image', ['id'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('is_artist', sa.Boolean(), nullable=False),
    sa.Column('is_moderator', sa.Boolean(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('artist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=320), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.Column('links', postgresql.ARRAY(sa.String()), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['image.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artist_name'), 'artist', ['name'], unique=False)
    op.create_index(op.f('ix_artist_user_id'), 'artist', ['user_id'], unique=False)
    op.create_table('festival',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=70), nullable=False),
    sa.Column('description', sa.String(length=320), nullable=True),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.Column('links', sa.ARRAY(sa.String()), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['image.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_festival_name'), 'festival', ['name'], unique=False)
    op.create_table('moderator',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_moderator_user_id'), 'moderator', ['user_id'], unique=False)
    op.create_table('artist_like',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artist_like_artist_id'), 'artist_like', ['artist_id'], unique=False)
    op.create_table('artwork',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('year_created', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('links', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('added_by_user_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('festival_id', sa.Integer(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('EXISTING', 'DESTROYED', 'OVERPAINTED', name='artworkstatus'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['added_by_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['festival_id'], ['festival.id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['artwork_location.id'], use_alter=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artwork_id'), 'artwork', ['id'], unique=False)
    op.create_index(op.f('ix_artwork_title'), 'artwork', ['title'], unique=False)
    op.create_table('festival_like',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('festival_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['festival_id'], ['festival.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_festival_like_festival_id'), 'festival_like', ['festival_id'], unique=False)
    op.create_table('ticket',
    sa.Column('discriminator', sa.String(length=50), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('object_class', sa.Enum('ARTWORK', 'ARTIST', 'FESTIVAL', name='ticketavailableobjectclasses'), nullable=False),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('moderator_id', sa.Integer(), nullable=True),
    sa.Column('ticket_type', sa.Enum('CREATE', 'EDIT', 'COMPLAIN', name='tickettype'), nullable=False),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='ticketstatus'), nullable=True),
    sa.Column('moderator_comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['moderator_id'], ['moderator.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ticket_id'), 'ticket', ['id'], unique=False)
    op.create_index(op.f('ix_ticket_user_id'), 'ticket', ['user_id'], unique=False)
    op.create_table('artwork_like',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('artwork_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artwork_id'], ['artwork.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artwork_like_artwork_id'), 'artwork_like', ['artwork_id'], unique=False)
    op.create_table('artwork_moderation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artwork_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='artworkmoderationstatus'), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['artwork_id'], ['artwork.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('artwork_id')
    )
    op.create_index(op.f('ix_artwork_moderation_id'), 'artwork_moderation', ['id'], unique=False)
    op.create_table('image_artwork',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artwork_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artwork_id'], ['artwork.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id'], ['image.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('image_ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ticket_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['image.id'], ),
    sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ticket_artwork',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artwork_data', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['ticket.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artwork_location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('thumbnail_image_id', sa.Integer(), nullable=True),
    sa.Column('artwork_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artwork_id'], ['artwork.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['thumbnail_image_id'], ['image_artwork.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('artwork_id')
    )
    op.create_index(op.f('ix_artwork_location_id'), 'artwork_location', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_artwork_location_id'), table_name='artwork_location')
    op.drop_table('artwork_location')
    op.drop_table('ticket_artwork')
    op.drop_table('image_ticket')
    op.drop_table('image_artwork')
    op.drop_index(op.f('ix_artwork_moderation_id'), table_name='artwork_moderation')
    op.drop_table('artwork_moderation')
    op.drop_index(op.f('ix_artwork_like_artwork_id'), table_name='artwork_like')
    op.drop_table('artwork_like')
    op.drop_index(op.f('ix_ticket_user_id'), table_name='ticket')
    op.drop_index(op.f('ix_ticket_id'), table_name='ticket')
    op.drop_table('ticket')
    op.drop_index(op.f('ix_festival_like_festival_id'), table_name='festival_like')
    op.drop_table('festival_like')
    op.drop_index(op.f('ix_artwork_title'), table_name='artwork')
    op.drop_index(op.f('ix_artwork_id'), table_name='artwork')
    op.drop_table('artwork')
    op.drop_index(op.f('ix_artist_like_artist_id'), table_name='artist_like')
    op.drop_table('artist_like')
    op.drop_index(op.f('ix_moderator_user_id'), table_name='moderator')
    op.drop_table('moderator')
    op.drop_index(op.f('ix_festival_name'), table_name='festival')
    op.drop_table('festival')
    op.drop_index(op.f('ix_artist_user_id'), table_name='artist')
    op.drop_index(op.f('ix_artist_name'), table_name='artist')
    op.drop_table('artist')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_image_id'), table_name='image')
    op.drop_table('image')
    # ### end Alembic commands ###

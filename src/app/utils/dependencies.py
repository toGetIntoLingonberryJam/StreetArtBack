from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from starlette import status

from app.api.routes.common import generate_detail, ErrorCode
from app.modules.artists.models import Artist
from app.modules.users.fastapi_users_config import current_user
from app.modules.users.models import User
from app.services.artist import ArtistsService
from app.services.moderator import ModeratorsService
from app.utils.unit_of_work import UnitOfWork

UOWDep = Annotated[UnitOfWork, Depends(UnitOfWork)]


async def get_current_artist(uow: UOWDep, user: User = Depends(current_user)):
    artist = await ArtistsService().get_artist_by_user_id(uow, user.id)
    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=generate_detail(
                error_code=ErrorCode.NO_ACCESS_TO_RESOURCE,
                message="You don't have access",
            ),
        )
    return artist


current_artist = Annotated[Artist, Depends(get_current_artist)]


async def get_current_moderator(uow: UOWDep, user: User = Depends(current_user)):
    try:
        moderator = await ModeratorsService.get_moderator_by_user_id(
            uow=uow, user_id=user.id
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=generate_detail(
                error_code=ErrorCode.NO_ACCESS_TO_RESOURCE,
                message="You don't have access",
            ),
        )

    return moderator


current_moderator = Annotated[Artist, Depends(get_current_moderator)]

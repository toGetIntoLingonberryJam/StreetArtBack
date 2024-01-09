from app.api.utils import remove_trailing_slashes_from_routes
from fastapi import APIRouter

from . import auth, users, artworks, tickets

router = APIRouter(prefix="/v1", include_in_schema=True)

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(artworks.router)
router.include_router(tickets.router)

# Удаляем последний слэш в путях
router = remove_trailing_slashes_from_routes(router)

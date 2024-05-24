# from . import auth, users, artworks, artists, festivals, collection, geo, support
from ..utils.custom_router import CustomAPIRouter
from ..utils.utils import remove_trailing_slashes_from_routes
from .artists import router as artists_router
from .artworks import router as artworks_router
from .auth import router as auth_router
from .collection import router as collection_router
from .festivals import router as festivals_router
from .geo import router as geo_router
from .support import router as support_router
from .users import router as users_router

router = CustomAPIRouter(prefix="/v1", include_in_schema=True)

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(artworks_router)
router.include_router(artists_router)
router.include_router(festivals_router)
router.include_router(collection_router)
router.include_router(geo_router)
router.include_router(support_router)

# Удаляем последний слэш в путях
router = remove_trailing_slashes_from_routes(router)

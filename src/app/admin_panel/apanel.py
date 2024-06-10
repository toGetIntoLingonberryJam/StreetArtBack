from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine

from app.admin_panel.admin_view import *
from app.admin_panel.apanel_auth import AdminAuth
from config import settings


class AdminPanel:
    admin: Admin

    def _add_views(self):
        views = [
            # UserAdmin,
            # ArtistAdmin,
            # ModeratorAdmin,
            # ArtworkAdmin,
            # ImageArtworkAdmin,
            # ArtworkLocationAdmin,
            # TicketArtworkAdmin,
            # TicketBaseAdmin,
            # ImageAdmin,
        ]

        for view in views:
            self.admin.add_view(view)

    def __init__(self, app: FastAPI, engine: AsyncEngine):
        self.admin = Admin(
            app,
            engine,
            title="StreetArt",
            authentication_backend=AdminAuth(
                secret_key=settings.secret_verification_token
            ),
        )
        self._add_views()

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine

from config import get_settings
from app.admin_panel.admin_view import *
from app.admin_panel.apanel_auth import AdminAuth


class AdminPanel:
    admin: Admin

    def __init__(self, app: FastAPI, engine: AsyncEngine):
        self.admin = Admin(
            app,
            engine,
            title="StreetArt",
            authentication_backend=AdminAuth(
                secret_key=get_settings().secret_verification_token
            ),
        )

        self.admin.add_view(UserAdmin)

        self.admin.add_view(ArtworkAdmin)
        self.admin.add_view(ArtworkImageAdmin)
        self.admin.add_view(ArtworkLocationAdmin)
        self.admin.add_view(ArtworkModerationAdmin)

        self.admin.add_view(ArtworkTicketAdmin)
        self.admin.add_view(BaseTicketAdmin)

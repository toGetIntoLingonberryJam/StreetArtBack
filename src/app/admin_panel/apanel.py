from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine

from app.admin_panel.admin_view import *


class AdminPanel:
    admin: Admin

    def __init__(self, app: FastAPI, engine: AsyncEngine):
        self.admin = Admin(app, engine, title="StreetArt")

        self.admin.add_view(UserAdmin)

        self.admin.add_view(ArtworkAdmin)
        self.admin.add_view(ArtworkAdditionsAdmin)
        self.admin.add_view(ArtworkImageAdmin)
        self.admin.add_view(ArtworkLocationAdmin)
        self.admin.add_view(ArtworkModerationAdmin)

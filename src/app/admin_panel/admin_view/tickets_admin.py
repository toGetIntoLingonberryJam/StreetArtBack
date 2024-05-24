from sqladmin import ModelView

from app.modules.tickets.models import TicketBase
from app.modules.tickets.models.ticket_artwork import TicketArtwork

DROPDOWN_CATEGORY = "Тикет"


class TicketArtworkAdmin(ModelView, model=TicketArtwork):
    column_list = "__all__"
    category = DROPDOWN_CATEGORY


class TicketBaseAdmin(ModelView, model=TicketBase):
    column_list = "__all__"
    category = DROPDOWN_CATEGORY

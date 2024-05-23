from typing import TypeVar

from app.modules.tickets.schemas.ticket_artwork import (
    TicketArtworkCreateSchema,
    TicketArtworkReadSchema,
)
from app.modules.tickets.schemas.ticket_base import TicketCreateSchema, TicketReadSchema

# from app.modules.tickets.utils.classes import TicketRegistry
#
# TicketsModelType = TypeVar(
#     "TicketsModelType", **TicketRegistry.ticket_classes.values()
# )  # TicketBase, TicketArtwork

TicketReadSchemaType = TypeVar(
    "TicketReadSchemaType", TicketArtworkReadSchema, TicketReadSchema
)
TicketCreateSchemaType = TypeVar(
    "TicketCreateSchemaType", TicketArtworkCreateSchema, TicketCreateSchema
)


from typing import TypeVar

from app.modules.tickets.schemas.ticket_base import TicketCreateSchema, TicketReadSchema

from app.modules.tickets.schemas.ticket_artwork import (
    ArtworkTicketCreateSchema,
    ArtworkTicketReadSchema,
)

TicketReadSchemaType = TypeVar(
    "TicketReadSchemaType", ArtworkTicketReadSchema, TicketReadSchema
)
TicketCreateSchemaType = TypeVar(
    "TicketCreateSchemaType", ArtworkTicketCreateSchema, TicketCreateSchema
)
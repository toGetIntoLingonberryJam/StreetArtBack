import enum


# Enum и базовая модель Ticket
class TicketType(str, enum.Enum):
    CREATE = "create"
    EDIT = "edit"
    COMPLAIN = "complain"


class TicketStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class TicketModel(str, enum.Enum):
    TICKET = "ticket"
    ARTWORK_TICKET = "artwork_ticket"


class TicketRegistry:
    ticket_classes = {}

    @classmethod
    def register(cls, ticket_model_value):
        def wrapper(ticket_class):
            cls.ticket_classes[ticket_model_value] = ticket_class
            return ticket_class

        return wrapper

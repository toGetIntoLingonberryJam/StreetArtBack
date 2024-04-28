import enum


# Enum и базовая модель Ticket
class TicketRegistry:
    """
    Реестр классов тикетов. Используется для регистрации различных типов тикетов.
    """
    ticket_classes = {}

    @classmethod
    def register(cls, ticket_model_value):
        """
        Регистрирует класс тикета в реестре.
        """
        def wrapper(ticket_class):
            cls.ticket_classes[ticket_model_value] = ticket_class
            return ticket_class

        return wrapper


class TicketType(str, enum.Enum):
    CREATE = "create"  # Создание
    EDIT = "edit"  # Редактирование
    COMPLAIN = "complain"  # Жалоба


class TicketStatus(enum.Enum):
    PENDING = "pending"  # В ожидании
    ACCEPTED = "accepted"  # Одобрено
    REJECTED = "rejected"  # Отклонено


class TicketModel(str, enum.Enum):
    TICKET = "ticket"
    ARTWORK_TICKET = "artwork_ticket"

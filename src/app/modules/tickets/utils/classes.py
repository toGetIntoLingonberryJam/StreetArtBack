import enum

from app.modules.models import Artist, Artwork, Festival


# Enum и базовая модель Ticket
class TicketRegistry:
    """
    Реестр классов тикетов.
    Над каждой моделью тикетов расположен декоратор. И в момент запуска приложения в словарь добавляется тикет.
    Используется в методе валидации TicketsRepository._validate_and_get_ticket_model_class
    Своеобразный посредник, благодаря которому мы на 100% можем быть уверены, что модель действительно существует,
    а не является просто строковым объектом в enum TicketModel
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


class TicketModel(str, enum.Enum):
    TICKET = "ticket"
    TICKET_ARTWORK = "ticket_artwork"


class TicketType(str, enum.Enum):
    CREATE = "create"  # Создание
    EDIT = "edit"  # Редактирование
    COMPLAIN = "complain"  # Жалоба


class TicketStatus(str, enum.Enum):
    PENDING = "pending"  # В ожидании
    APPROVED = "approved"  # Одобрено
    REJECTED = "rejected"  # Отклонено


# Для разграничения тикетов на редактирование: object_class + object_id
class TicketAvailableObjectClasses(str, enum.Enum):
    ARTWORK = "artwork"
    ARTIST = "artist"
    FESTIVAL = "festival"

    def get_class(self):
        if self == TicketAvailableObjectClasses.ARTWORK:
            from app.modules.models import Artwork

            return Artwork
        elif self == TicketAvailableObjectClasses.ARTIST:
            from app.modules.models import Artist

            return Artist
        elif self == TicketAvailableObjectClasses.FESTIVAL:
            from app.modules.models import Festival

            return Festival
        else:
            raise ValueError("Invalid enum value")

import logging


def create_logger(name: str) -> logging.Logger:
    new_logger = logging.getLogger(name)
    if not new_logger.hasHandlers():  # Предотвращает добавление множества обработчиков
        new_logger.setLevel(logging.DEBUG)

        # Создание консольного обработчика
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Создание форматтера и добавление его к обработчику
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)

        # Добавление обработчика к логгеру
        new_logger.addHandler(ch)

    return new_logger


# Глобальный логгер для использования везде
logger = create_logger(__name__)

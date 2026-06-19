import enum


class BookingStatus(str, enum.Enum):
    """
    Статусы бронирования.

    Наследуемся от str, чтобы Pydantic и БД могли сериализовать значения без .value.
    """

    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

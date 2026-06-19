from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants import BookingStatus


class BookingCreate(BaseModel):
    """
    Схема для создания бронирования.

    Валидирует данные, которые присылает клиент.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description='Имя клиента',
    )
    meeting_time: datetime = Field(
        ...,
        description='Желаемые дата и время встречи',
    )
    service_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description='Тип услуги',
    )


class BookingResponse(BaseModel):
    """
    Схема для ответа API.

    Используется, когда отдаём данные клиенту.
    """

    id: int
    name: str
    meeting_time: datetime
    service_type: str
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingList(BaseModel):
    """
    Схема для списка бронирований с пагинацией.
    """

    items: list[BookingResponse]
    total: int
    page: int
    size: int
    pages: int

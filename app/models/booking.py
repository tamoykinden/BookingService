from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func

from app.constants import BookingStatus
from app.database import Base


class Booking(Base):
    """
    Модель бронирования.

    Хранит заявки на встречи в базе данных.
    """

    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, index=True, comment='ID')
    name = Column(String(255), nullable=False, comment='Имя клиента')
    meeting_time = Column(DateTime(timezone=True), nullable=False, comment='Желаемые дата и время встречи')
    service_type = Column(String(100), nullable=False, comment='Тип услуги')
    status = Column(
        SQLEnum(BookingStatus),
        default=BookingStatus.PENDING,
        nullable=False,
        comment='Статус бронирования',
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='Дата создания',
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment='Дата обновления',
    )

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import BookingStatus
from app.models.booking import Booking
from app.schemas.booking import BookingCreate


async def create_booking(db: AsyncSession, data: BookingCreate) -> Booking:
    """Создаёт новое бронирование в статусе PENDING."""

    booking = Booking(
        name=data.name,
        meeting_time=data.meeting_time,
        service_type=data.service_type,
        status=BookingStatus.PENDING,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


async def get_booking(db: AsyncSession, booking_id: int) -> Optional[Booking]:
    """Получает бронирование по ID."""

    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    return result.scalar_one_or_none()


async def get_bookings(
    db: AsyncSession,
    status: Optional[BookingStatus] = None,
    page: int = 1,
    size: int = 10,
) -> tuple[list[Booking], int]:
    """
    Получает список бронирований с фильтром по статусу и пагинацией.

    Returns:
        tuple: (список бронирований, общее количество)
    """
    query = select(Booking)

    if status:
        query = query.where(Booking.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Booking.created_at.desc())

    result = await db.execute(query)
    bookings = result.scalars().all()

    return bookings, total


async def update_booking_status(
    db: AsyncSession,
    booking: Booking,
    new_status: BookingStatus,
) -> Booking:
    """Обновляет статус бронирования."""

    booking.status = new_status
    await db.commit()
    await db.refresh(booking)
    return booking


async def cancel_booking(db: AsyncSession, booking: Booking) -> Booking:
    """Отменяет бронирование. Только если статус PENDING."""

    if booking.status != BookingStatus.PENDING:
        raise ValueError(
            f'Нельзя отменить бронь в статусе: {booking.status.value}'
        )
    return await update_booking_status(db, booking, BookingStatus.CANCELLED)

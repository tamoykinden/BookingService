from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.constants import BookingStatus
from app.depencies import get_db
from app.schemas.booking import BookingCreate, BookingList, BookingResponse
from app.tasks import process_booking

router = APIRouter(
    prefix='/bookings',
    tags=['bookings'],
)

limiter = Limiter(key_func=get_remote_address)

@router.post(
    '/',
    response_model=BookingResponse,
    status_code=201,
    summary='Создать бронирование',
)
@limiter.limit('5/minute')
async def create_booking(
    request: Request,
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Создаёт новое бронирование.

    Бронь создаётся в статусе pending и отправляется в очередь на обработку.
    """

    booking = await crud.create_booking(db, data)
    process_booking.delay(booking.id)
    return booking


@router.get(
    '/{booking_id}',
    response_model=BookingResponse,
    summary='Получить бронирование по ID',
)
async def get_booking(
    booking_id: int = Path(..., ge=1, description='ID бронирования'),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает бронирование по его ID."""

    booking = await crud.get_booking(db, booking_id)

    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f'Бронирование с id {booking_id} не найдено',
        )

    return booking


@router.get(
    '/',
    response_model=BookingList,
    summary='Получить список бронирований',
)
async def list_bookings(
    status: BookingStatus | None = Query(None, description='Фильтр по статусу'),
    page: int = Query(1, ge=1, description='Номер страницы'),
    size: int = Query(10, ge=1, le=100, description='Размер страницы'),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает список бронирований с фильтрацией и пагинацией."""

    bookings, total = await crud.get_bookings(db, status, page, size)

    return BookingList(
        items=bookings,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size),
    )


@router.delete(
    '/{booking_id}',
    status_code=204,
    summary='Отменить бронирование',
)
async def cancel_booking(
    booking_id: int = Path(..., ge=1, description='ID бронирования'),
    db: AsyncSession = Depends(get_db),
):
    """Отменяет бронирование (только в статусе pending)."""

    booking = await crud.get_booking(db, booking_id)

    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f'Бронирование с id {booking_id} не найдено',
        )

    try:
        await crud.cancel_booking(db, booking)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return None

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_booking(client: AsyncClient):
    """Проверяет создание бронирования."""

    response = await client.post('/bookings/', json={
        'name': 'Иван Петров',
        'meeting_time': '2026-06-20T15:00:00',
        'service_type': 'Консультация',
    })

    assert response.status_code == 201
    data = response.json()
    assert data['name'] == 'Иван Петров'
    assert data['status'] == 'pending'
    assert data['id'] == 1


@pytest.mark.asyncio
async def test_get_booking(client: AsyncClient):
    """Проверяет получение бронирования по ID."""

    await client.post('/bookings/', json={
        'name': 'Тест',
        'meeting_time': '2026-06-20T16:00:00',
        'service_type': 'Тест',
    })

    response = await client.get('/bookings/1')

    assert response.status_code == 200
    assert response.json()['id'] == 1


@pytest.mark.asyncio
async def test_get_booking_not_found(client: AsyncClient):
    """Проверяет 404 для несуществующей брони."""

    response = await client.get('/bookings/999')

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_bookings(client: AsyncClient):
    """Проверяет список бронирований."""

    await client.post('/bookings/', json={
        'name': 'Раз',
        'meeting_time': '2026-06-20T17:00:00',
        'service_type': 'Тест',
    })

    response = await client.get('/bookings/')

    assert response.status_code == 200
    data = response.json()
    assert 'items' in data
    assert 'total' in data
    assert data['total'] >= 1


@pytest.mark.asyncio
async def test_cancel_booking(client: AsyncClient):
    """Проверяет отмену бронирования."""

    await client.post('/bookings/', json={
        'name': 'Отмена',
        'meeting_time': '2026-06-20T18:00:00',
        'service_type': 'Тест',
    })

    response = await client.delete('/bookings/1')

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_invalid_data(client: AsyncClient):
    """Проверяет валидацию — пустые поля."""

    response = await client.post('/bookings/', json={
        'name': '',
        'meeting_time': 'не дата',
        'service_type': '',
    })

    assert response.status_code == 422

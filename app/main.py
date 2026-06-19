from fastapi import FastAPI

from app.routers.booking import router as bookings_router

app = FastAPI(
    title='Booking Service',
    description='Сервис для записи на встречи',
    version='1.0.0',
)

app.include_router(bookings_router)

@app.get('/health')
async def health_check():
    """Проверка работоспособности сервиса."""

    return {'status': 'ok'}

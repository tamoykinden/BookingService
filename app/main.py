from fastapi import FastAPI
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.routers.booking import router as bookings_router

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title='Booking Service',
    description='Сервис для записи на встречи',
    version='1.0.0',
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: __import__('fastapi').responses.JSONResponse(
    status_code=429,
    content={'detail': 'Слишком много запросов. Попробуйте позже.'},
))

app.include_router(bookings_router)

@app.get('/health')
async def health_check():
    """Проверка работоспособности сервиса."""

    return {'status': 'ok'}

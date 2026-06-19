from fastapi import FastAPI


app = FastAPI(
    title='Booking Service',
    description='Сервис для записи на встречи',
    version='1.0.0',
)


@app.get('/health')
async def health_check():
    """Проверка работоспособности сервиса."""

    return {'status': 'ok'}

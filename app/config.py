from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения.

    Читает переменные из .env файла и формирует URL для подключений.
    """

    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USER: str = 'user'
    DB_PASS: str = 'password'
    DB_NAME: str = 'booking_db'

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379

    @property
    def db_url(self) -> str:
        """Формирует URL для подключения к PostgreSQL."""

        return (
            f'postgresql://{self.DB_USER}:{self.DB_PASS}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    @property
    def celery_broker_url(self) -> str:
        """Формирует URL для Celery брокера (Redis)."""

        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0'

    @property
    def redis_result_url(self) -> str:
        """Формирует URL для Celery result backend (Redis)."""

        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0'

    class Config:
        env_file = '.env'


settings = Settings()

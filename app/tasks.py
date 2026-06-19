import json
import logging
import random
import time

from celery import Task

from app.celery_app import celery_app
from app.constants import BookingStatus
from app.database import sync_session
from app.models.booking import Booking


class JsonFormatter(logging.Formatter):

    """Форматирует логи в JSON."""

    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        return json.dumps(log_entry, ensure_ascii=False)


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=2,
    retry_backoff=True,
    autoretry_for=(Exception,),
)
def process_booking(self, booking_id: int):

    """
    Обрабатывает бронирование.

    Имитирует вызов внешнего сервиса:
    - 85% успех: статус confirmed, логируется уведомление
    - 15% ошибка: статус failed

    Идемпотентность: проверяет статус перед обработкой.
    """

    db = sync_session()

    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()

        if not booking:
            logger.error(json.dumps({
                'event': 'booking_not_found',
                'booking_id': booking_id,
            }))
            return

        if booking.status != BookingStatus.PENDING:
            logger.info(json.dumps({
                'event': 'booking_already_processed',
                'booking_id': booking_id,
                'status': booking.status.value,
            }))
            return

        time.sleep(0.5)

        if random.random() < 0.15:
            booking.status = BookingStatus.FAILED
            db.commit()
            logger.warning(json.dumps({
                'event': 'booking_failed',
                'booking_id': booking_id,
            }))
            raise Exception('Ошибка внешнего сервиса')
        else:
            booking.status = BookingStatus.CONFIRMED
            db.commit()
            logger.info(json.dumps({
                'event': 'booking_confirmed',
                'booking_id': booking_id,
                'client': booking.name,
            }))
            return {'status': 'confirmed', 'booking_id': booking_id}

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

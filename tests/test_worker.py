from unittest.mock import patch, MagicMock

from app.tasks import process_booking


@patch('app.tasks.json.dumps')
@patch('app.tasks.sync_session')
def test_process_booking_idempotent(mock_session, mock_json_dumps):
    """Проверяет, что задача не обрабатывает уже обработанную бронь."""

    mock_json_dumps.return_value = '{}'

    mock_booking = MagicMock()
    mock_booking.status = 'confirmed'

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_booking
    mock_session.return_value = mock_db

    result = process_booking(1)

    assert result is None
    mock_db.commit.assert_not_called()


@patch('app.tasks.json.dumps')
@patch('app.tasks.random.random')
@patch('app.tasks.sync_session')
def test_process_booking_success(mock_session, mock_random, mock_json_dumps):
    """Проверяет успешную обработку брони."""

    mock_json_dumps.return_value = '{}'
    mock_random.return_value = 0.5

    mock_booking = MagicMock()
    mock_booking.status = 'pending'
    mock_booking.name = 'Тест'

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_booking
    mock_session.return_value = mock_db

    result = process_booking(1)

    assert result['status'] == 'confirmed'
    assert mock_db.commit.called

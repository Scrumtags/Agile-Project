import pytest
from unittest.mock import patch, mock_open

from studybuddy import Database_Controller, Main

@pytest.fixture
def app():
    db_controller = Database_Controller()
    yield db_controller
    db_controller.conn.close()

def test_create_schedule(app):
    data = {
        'title': 'Test Title',
        'description': 'Test Description',
        'start_date': '2023-05-07',
        'end_date': '2023-05-07',
        'days_of_week': None
    }

    c = app.conn.cursor()
    c.execute("INSERT INTO schedules (title, description, start_date, end_date, days_of_week) VALUES (?, ?, ?, ?, ?)",
              (data['title'], data['description'], data['start_date'], data['end_date'], data['days_of_week']))

    event_id = c.lastrowid
    query = "SELECT * FROM schedules WHERE schedule_id = ?"
    params = (event_id, )
    result = c.execute(query, params).fetchone()

    assert result is not None
    assert result[1] == data['title']
    assert result[2] == data['description']
    assert result[3] == data['start_date']
    assert result[4] == data['end_date']
    assert result[5] == data['days_of_week']

def test_edit_schedule(app):
    data = {
        'title': 'Test Title',
        'description': 'Test Description',
        'start_date': '2023-05-07',
        'end_date': '2023-05-07',
        'days_of_week': None
    }

    c = app.conn.cursor()
    c.execute("INSERT INTO schedules (title, description, start_date, end_date, days_of_week) VALUES (?, ?, ?, ?, ?)",
              (data['title'], data['description'], data['start_date'], data['end_date'], data['days_of_week']))

    event_id = c.lastrowid

    updated_data = {
        'schedule_id': event_id,
        'title': 'Updated Schedule',
        'description': 'Updated Description',
        'start_date': '2023-05-11',
        'end_date': '2023-05-12',
        'days_of_week': None
    }

    app.edit_schedule(updated_data)

    query = "SELECT * FROM schedules WHERE schedule_id = ?"
    params = (event_id,)
    result = app.conn.execute(query, params).fetchone()

    assert result is not None
    assert result[1] == updated_data['title']
    assert result[2] == updated_data['description']
    assert result[3] == updated_data['start_date']
    assert result[4] == updated_data['end_date']
    assert result[5] == updated_data['days_of_week']

def test_delete_schedule(app):
    data = {
        'title': 'Test Title',
        'description': 'Test Description',
        'start_date': '2023-05-07',
        'end_date': '2023-05-07',
        'days_of_week': None
    }

    c = app.conn.cursor()
    c.execute("INSERT INTO schedules (title, description, start_date, end_date, days_of_week) VALUES (?, ?, ?, ?, ?)",
              (data['title'], data['description'], data['start_date'], data['end_date'], data['days_of_week']))

    event_id = c.lastrowid

    app.delete_schedule(event_id)

    query = "SELECT * FROM schedules WHERE schedule_id = ?"
    params = (event_id,)
    result = app.conn.execute(query, params).fetchone()

    assert result is None
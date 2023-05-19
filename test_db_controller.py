import pytest
import sqlite3
from studybuddy import Database_Controller

@pytest.fixture
def db_controller():
    db = Database_Controller()
    yield db
    db.conn.close()

def test_create_event(db_controller):
    data = {
        'title': 'Test Event',
        'description': 'Test Description',
        'start_date': '2023-05-10',
        'end_date': '2023-05-10',
        'completion_status': 0
    }

    db_controller.create_event(data)

    query = "SELECT * FROM events WHERE title = ?"
    params = (data['title'],)
    result = db_controller.conn.execute(query, params).fetchone()

    assert result is not None
    assert result[1] == data['title']
    assert result[2] == data['description']
    assert result[3] == data['start_date']
    assert result[4] == data['end_date']
    assert result[5] == data['completion_status']

def test_delete_event(db_controller):
    event_id = 1

    db_controller.delete_event(event_id)

    query = "SELECT * FROM events WHERE event_id = ?"
    params = (event_id,)
    result = db_controller.conn.execute(query, params).fetchone()

    assert result is None

def test_update_event(db_controller):
    updated_data = {
        'event_id': 2,
        'title': 'Updated Event',
        'tags': 'Updated Tags',
        'description': 'Updated Description',
        'start_date': '2023-05-11',
        'end_date': '2023-05-12',
        'completion_status': 1
    }

    event_id = updated_data['event_id']
    db_controller.update_event(updated_data)

    query = "SELECT * FROM events WHERE event_id = ?"
    params = (event_id,)
    result = db_controller.conn.execute(query, params).fetchone()

    assert result is not None
    assert result[1] == updated_data['title']
    assert result[2] == updated_data['description']
    assert result[3] == updated_data['start_date']
    assert result[4] == updated_data['end_date']
    assert result[5] == updated_data['completion_status']

def test_create_tables(db_controller):
    db_controller.create_tables()

    cursor = db_controller.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]

    assert 'events' in table_names
    assert 'tags' in table_names
    assert 'event_tags' in table_names
    assert 'schedules' in table_names
    assert 'schedule_tags' in table_names

def test_create_connection(db_controller):
    result = db_controller.create_connection()

    assert result is not None
    assert isinstance(result, sqlite3.Connection)
    assert result.in_transaction == False

def test_get_event_tags(db_controller):
    event_id = 1

    result = db_controller.get_event_tags(event_id)

    assert result is not None

def test_get_tags(db_controller):
    tag_ids = [(1, 2, 3)]

    result = db_controller.get_tags(tag_ids)

    assert len(result) == len(tag_ids)


def test_get_all_tags(db_controller):
    result = db_controller.get_all_tags()

    assert result is not None

def test_search_data(db_controller):
    check = "completion_status"
    searchText = "Completed"
    
    result = db_controller.search_data(check, searchText)

    assert result is not None

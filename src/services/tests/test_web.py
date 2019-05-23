import json
import uuid
import pytest
from config import Config
from web import app
from db import DB
import sys
import os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

@pytest.fixture
def client():
    app.config.from_object(Config)
    app.config.TESTING = True
    client = app.test_client()

    db = DB(app.config['PG_CONNECTION_URI'])
    db.conn.autocommit = True

    cursor = db.conn.cursor()
    cursor.execute(open("tests/db-test.sql", "r").read())
    cursor.close()

    db.close()

    yield client

def test_pending(client):
    rv = client.get('/photos/pending')
    assert rv.status == '200 OK'

def test_pending_response_size(client):
    rv = client.get('/photos/pending')
    json = rv.get_json()
    assert len(json) == 6

def test_pending_response_fields(client):
    rv = client.get('/photos/pending')
    json = rv.get_json()
    assert all (k in json[0] for k in ('created_at', 'status', 'url', 'uuid'))

def test_process_valid_uuid(client):
    rv = client.post('/photos/process',
                     data=json.dumps([str(uuid.uuid1())]),
                     content_type='application/json')
    assert rv.status == '202 ACCEPTED'

def test_process_empty(client):
    rv = client.post('/photos/process',
                     data=json.dumps([]),
                     content_type='application/json')
    assert rv.status == '400 BAD REQUEST'

def test_process_invalid_uuid(client):
    rv = client.post('/photos/process',
                     data=json.dumps(['a']),
                     content_type='application/json')
    assert rv.status == '400 BAD REQUEST'

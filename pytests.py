from flask import json
import pytest
from .app import app
from collections import Mapping


def seed_users(client):
    client.post('/user', data=json.dumps({"username" : "test1", "first_name" : "t", "last_name" : "1", "password" : "test1", "email" : "test1@gmail", "id" : "101"}),
                content_type='application/json')


@pytest.fixture
def client():
    client = app.test_client()
    seed_users(client)
    return client
"""Integration suite: real PostgreSQL test database, rebuilt before every test."""

import pytest


@pytest.fixture(autouse=True)
def _isolated_database(fresh_db):
    yield

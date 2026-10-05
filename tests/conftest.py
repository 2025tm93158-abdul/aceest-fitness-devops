import sys
from datetime import date
from pathlib import Path

import pytest

# Make the project root importable when running `pytest` from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402


@pytest.fixture
def client():
    """A fresh app (empty store) and a fixed 'today' for every test."""
    app = create_app({"TESTING": True, "TODAY": date(2026, 10, 4)})
    return app.test_client()


@pytest.fixture
def new_client(client):
    """Create one client through the API and return its JSON."""
    resp = client.post("/clients", json={
        "name": "Abdul", "age": 28, "height_cm": 175,
        "weight_kg": 70, "program": "FL",
    })
    assert resp.status_code == 201
    return resp.get_json()

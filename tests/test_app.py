"""
Tests for the Mergington High School API.

Usage:
    $ pytest

Each test exercises one of the six behaviours described in the
exercise:
  * listing activities
  * successful signup
  * signup for non‑existent activity
  * signup when already registered
  * successful removal
  * removal of a non‑existent participant

A pytest fixture resets the in‑memory `activities` dict before every
test using `copy.deepcopy`.
"""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities  # import the FastAPI app and the shared dict

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Preserve the original activities data and restore it after each test.

    The fixture is marked `autouse=True` so it runs for every test function
    without having to be explicitly requested.
    """
    original = copy.deepcopy(activities)
    yield
    # clear and restore to avoid reassigning the imported reference
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_all():
    """GET /activities should return the full activities dictionary."""
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic sanity check
    assert "Chess Club" in data
    assert isinstance(data, dict)


def test_signup_for_activity_success():
    """POST to signup should add a new participant."""
    email = "newstudent@mergington.edu"
    resp = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity():
    """Signing up for a non‑existent activity returns 404."""
    resp = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_signup_already_signed_up():
    """Attempting to sign up a student already enrolled yields 400."""
    existing = activities["Chess Club"]["participants"][0]
    resp = client.post("/activities/Chess Club/signup", params={"email": existing})
    assert resp.status_code == 400


def test_remove_participant_success():
    """DELETE should remove an existing participant."""
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_found():
    """Removing a non‑existent participant returns 404."""
    resp = client.delete(
        "/activities/Chess Club/participants", params={"email": "unknown@mergington.edu"}
    )
    assert resp.status_code == 404

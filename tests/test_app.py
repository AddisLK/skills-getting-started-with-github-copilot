import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Mergington High School" in response.text


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_for_activity_adds_participant():
    payload_email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": payload_email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {payload_email} for Chess Club"
    assert payload_email in activities["Chess Club"]["participants"]


def test_signup_duplicate_student_returns_bad_request():
    duplicate_email = "michael@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": duplicate_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_nonexistent_activity_returns_not_found():
    response = client.post("/activities/NotRealActivity/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

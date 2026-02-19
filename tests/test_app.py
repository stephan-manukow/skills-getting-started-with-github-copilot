from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


def test_get_activities_returns_initial_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    activity_path = quote(activity_name, safe="")

    response = client.post(f"/activities/{activity_path}/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant():
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]
    activity_path = quote(activity_name, safe="")

    response = client.post(f"/activities/{activity_path}/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_succeeds():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    activity_path = quote(activity_name, safe="")

    response = client.delete(
        f"/activities/{activity_path}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]

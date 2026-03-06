import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


def _activity_path(activity_name: str) -> str:
    return quote(activity_name, safe="")


@pytest.fixture(autouse=True)
def restore_activities_state():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_data_and_cache_header(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert response.headers.get("cache-control") == "no-store"
    assert expected_activity in payload
    assert isinstance(payload[expected_activity]["participants"], list)


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{_activity_path(activity_name)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{_activity_path(activity_name)}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{_activity_path(unknown_activity)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_all_case_variants(client):
    # Arrange
    activity_name = "Chess Club"
    app_module.activities[activity_name]["participants"].extend(
        ["DeleteMe@mergington.edu", "deleteme@mergington.edu"]
    )
    email_to_remove = "DELETEME@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{_activity_path(activity_name)}/participants",
        params={"email": email_to_remove},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email_to_remove} from {activity_name}"
    assert all(
        participant.lower() != "deleteme@mergington.edu"
        for participant in app_module.activities[activity_name]["participants"]
    )


def test_unregister_returns_404_when_participant_not_found(client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{_activity_path(activity_name)}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{_activity_path(unknown_activity)}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# Keep a pristine copy so we can reset between tests
_ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange (reset state)
    activities.clear()
    activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_200_and_includes_known_activity(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert "Programming Class" in data


def test_signup_adds_participant_and_returns_message(client):
    # Arrange
    activity = "Chess Club"
    email = "tester@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_existing_email_returns_400(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_removes_and_returns_success_message(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_delete_non_existing_participant_returns_404(client):
    # Arrange
    activity = "Chess Club"
    email = "nope@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"

"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that getting activities returns 200 OK"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self):
        """Test that getting activities returns all activities"""
        response = client.get("/activities")
        activities = response.json()
        
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert "Basketball" in activities
        assert "Tennis Club" in activities
        assert "Drama Club" in activities

    def test_activity_structure(self):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_returns_200(self):
        """Test that signing up for an activity returns 200 OK"""
        response = client.post("/activities/Basketball/signup?email=test@mergington.edu")
        assert response.status_code == 200

    def test_signup_adds_participant(self):
        """Test that signing up adds the participant to the activity"""
        # First, get the initial count
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before["Basketball"]["participants"])
        
        # Sign up a new participant
        email = "newstudent@mergington.edu"
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 200
        
        # Verify the participant was added
        activities_after = client.get("/activities").json()
        final_count = len(activities_after["Basketball"]["participants"])
        assert final_count == initial_count + 1
        assert email in activities_after["Basketball"]["participants"]

    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        email = "success@mergington.edu"
        response = client.post(f"/activities/Tennis%20Club/signup?email={email}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_signup_duplicate_participant_returns_400(self):
        """Test that signing up twice with same email returns 400"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Basketball/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Basketball/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signing up for a nonexistent activity returns 404"""
        response = client.post("/activities/NonexistentActivity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_returns_200(self):
        """Test that unregistering returns 200 OK"""
        email = "unregister@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Basketball/signup?email={email}")
        
        # Then unregister
        response = client.delete(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 200

    def test_unregister_removes_participant(self):
        """Test that unregistering removes the participant"""
        email = "removetest@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Drama%20Club/signup?email={email}")
        activities_before = client.get("/activities").json()
        assert email in activities_before["Drama Club"]["participants"]
        
        # Unregister
        client.delete(f"/activities/Drama%20Club/signup?email={email}")
        
        # Verify removed
        activities_after = client.get("/activities").json()
        assert email not in activities_after["Drama Club"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregistering from nonexistent activity returns 404"""
        response = client.delete("/activities/FakeActivity/signup?email=test@mergington.edu")
        assert response.status_code == 404

    def test_unregister_not_signed_up_returns_400(self):
        """Test that unregistering when not signed up returns 400"""
        response = client.delete("/activities/Basketball/signup?email=notsigndup@mergington.edu")
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_returns_success_message(self):
        """Test that unregister returns a success message"""
        email = "successunreg@mergington.edu"
        
        # Sign up first
        client.post(f"/activities/Art%20Studio/signup?email={email}")
        
        # Then unregister
        response = client.delete(f"/activities/Art%20Studio/signup?email={email}")
        data = response.json()
        assert "message" in data
        assert email in data["message"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

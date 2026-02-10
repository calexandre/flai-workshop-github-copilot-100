"""
Tests for the Mergington High School API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis instruction and friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["sarah@mergington.edu", "maya@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Orchestra and band performance group",
            "schedule": "Mondays and Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Debate Club": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["henry@mergington.edu", "grace@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "STEM competition and scientific exploration",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["ryan@mergington.edu"]
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that all expected activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert "Art Studio" in data
        assert "Music Ensemble" in data
        assert "Debate Club" in data
        assert "Science Olympiad" in data
    
    def test_activities_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_existing_activity(self, client):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up test@mergington.edu for Chess Club"
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_student(self, client):
        """Test that signing up the same student twice fails"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Tennis Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Tennis Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Student already signed up"
    
    def test_signup_preserves_existing_participants(self, client):
        """Test that signing up doesn't remove existing participants"""
        # Get initial participants
        activities_response = client.get("/activities")
        initial_participants = activities_response.json()["Art Studio"]["participants"]
        initial_count = len(initial_participants)
        
        # Sign up new student
        response = client.post(
            "/activities/Art Studio/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify all original participants are still there plus the new one
        activities_response = client.get("/activities")
        current_participants = activities_response.json()["Art Studio"]["participants"]
        assert len(current_participants) == initial_count + 1
        for participant in initial_participants:
            assert participant in current_participants


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_student(self, client):
        """Test successful unregistration of a signed up student"""
        email = "james@mergington.edu"
        
        # Verify student is initially signed up
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Basketball Team"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Basketball Team/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from Basketball Team"
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Basketball Team"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_non_signed_up_student(self, client):
        """Test unregistering a student who isn't signed up fails"""
        response = client.delete(
            "/activities/Music Ensemble/unregister?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"
    
    def test_unregister_preserves_other_participants(self, client):
        """Test that unregistering doesn't affect other participants"""
        # Get initial participants for Debate Club
        activities_response = client.get("/activities")
        initial_participants = activities_response.json()["Debate Club"]["participants"].copy()
        
        # Unregister one student
        email_to_remove = initial_participants[0]
        remaining_participants = [p for p in initial_participants if p != email_to_remove]
        
        response = client.delete(
            f"/activities/Debate Club/unregister?email={email_to_remove}"
        )
        assert response.status_code == 200
        
        # Verify only the specified student was removed
        activities_response = client.get("/activities")
        current_participants = activities_response.json()["Debate Club"]["participants"]
        assert email_to_remove not in current_participants
        for participant in remaining_participants:
            assert participant in current_participants


class TestIntegration:
    """Integration tests for multiple operations"""
    
    def test_signup_and_unregister_flow(self, client):
        """Test the complete flow of signing up and unregistering"""
        email = "fullflow@mergington.edu"
        activity = "Science Olympiad"
        
        # Get initial count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        assert len(activities_response.json()[activity]["participants"]) == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]
        assert len(activities_response.json()[activity]["participants"]) == initial_count
    
    def test_multiple_students_signup_different_activities(self, client):
        """Test multiple students signing up for different activities"""
        signups = [
            ("student1@mergington.edu", "Chess Club"),
            ("student2@mergington.edu", "Programming Class"),
            ("student3@mergington.edu", "Gym Class"),
        ]
        
        for email, activity in signups:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for email, activity in signups:
            assert email in activities_data[activity]["participants"]

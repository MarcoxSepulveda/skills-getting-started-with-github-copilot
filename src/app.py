"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
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
    "Soccer Team": {
        "description": "Team training, drills, and inter-school soccer matches",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball fundamentals and compete in school leagues",
        "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["ava@mergington.edu", "lucas@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and mixed-media art projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["mia@mergington.edu", "isabella@mergington.edu"]
    },
    "School Choir": {
        "description": "Vocal training and group performances at school events",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 4:30 PM",
        "max_participants": 25,
        "participants": ["charlotte@mergington.edu", "james@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop critical thinking and public speaking through debates",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
    },
    "Robotics Club": {
        "description": "Design, build, and program robots for STEM competitions",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["henry@mergington.edu", "evelyn@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(response: Response):
    # Avoid stale activity data in browser caches.
    response.headers["Cache-Control"] = "no-store"
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants")
def unregister_participant(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized_email = email.strip().lower()

    # Remove all entries for this email in case duplicates exist
    remaining_participants = [
        participant for participant in activity["participants"]
        if participant.lower() != normalized_email
    ]
    removed_count = len(activity["participants"]) - len(remaining_participants)

    if removed_count == 0:
        raise HTTPException(status_code=404, detail="Participant not found in this activity")

    activity["participants"] = remaining_participants
    return {"message": f"Unregistered {email} from {activity_name}"}

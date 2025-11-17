# This module handles the Timeline events and data
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel 
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter()

class TimelineEvent(BaseModel):
    id: int
    title: str
    description: str 
    timestamp: datetime
    message: str
    type: str # Note/Audit

# In-memory storage for timeline events
TIMELINE_EVENTS = [
    TimelineEvent(id=1, title="Patient Admitted", description="Patient admitted to the hospital", timestamp=datetime.now() - timedelta(days=2), message="Patient John Doe admitted.", type="Audit"),
    TimelineEvent(id=2, title="Initial Assessment", description="Nurse performed initial assessment", timestamp=datetime.now() - timedelta(days=1, hours=5), message="Initial assessment completed by Nurse Jane.", type="Note"),
    TimelineEvent(id=3, title="Medication Administered", description="Administered prescribed medication", timestamp=datetime.now() - timedelta(hours=20), message="Administered 500mg of medication X.", type="Audit"),
    TimelineEvent(id=4, title="Follow-up Visit", description="Doctor's follow-up visit", timestamp=datetime.now() - timedelta(hours=10), message="Follow-up visit by Dr. Smith.", type="Note"),
    TimelineEvent(id=5, title="Discharge Planning", description="Planning for patient discharge", timestamp=datetime.now() - timedelta(hours=2), message="Discharge planning initiated.", type="Audit"),
    TimelineEvent(id=6, title="Patient Discharged", description="Patient discharged from the hospital", timestamp=datetime.now() - timedelta(minutes=30), message="Patient John Doe discharged.", type="Audit"),
    TimelineEvent(id=7, title="Post-Discharge Call", description="Nurse called patient post-discharge", timestamp=datetime.now() - timedelta(minutes=10), message="Post-discharge call completed.", type="Note"),
    TimelineEvent(id=8, title="Lab Results Received", description="Received lab results for patient", timestamp=datetime.now() - timedelta(hours=1), message="Lab results for patient John Doe received.", type="Audit"),
    TimelineEvent(id=9, title="Physical Therapy Session", description="Conducted physical therapy session", timestamp=datetime.now() - timedelta(hours=3), message="Physical therapy session completed.", type="Note"),
    TimelineEvent(id=10, title="Dietary Consultation", description="Dietary consultation with nutritionist", timestamp=datetime.now() - timedelta(hours=4), message="Dietary consultation conducted.", type="Note"),
    TimelineEvent(id=11, title="Medication Review", description="Reviewed patient's medications", timestamp=datetime.now() - timedelta(hours=6), message="Medication review completed.", type="Audit"),
    TimelineEvent(id=12, title="Vaccination Administered", description="Administered flu vaccination", timestamp=datetime.now() - timedelta(hours=8), message="Flu vaccination administered.", type="Audit")
]

# This endpoint retrieves timeline events with optional filtering and limiting
# Example: /timeline/?type=Audit&limit=5 will return the latest 5 Note events
# /timeline/?limit=3 will return the latest 3 events of any type
@router.get("/", response_model=List[TimelineEvent])
async def get_timeline(type: Optional[str] = Query(None, description="Filter by event type (Note/Audit)"),
                       limit: Optional[int] = Query(10, description="Limit the number of events returned")):
    
    events = TIMELINE_EVENTS.copy() # Start with all Events
    if type:
        events = [event for event in events if event.type == type] # Filter by type if provided

    events = sorted(events, key=lambda x: x.timestamp, reverse=True) # Sort by timestamp descending

    if limit:
        events = events[:limit] # Apply limit if provided
    
    return events

# This endpoint retrieves a specific timeline event by its ID
# Example: /timeline/3 will return the event with ID 3
@router.get("/{event_id}", response_model=TimelineEvent)
async def get_timeline_event(event_id: int):
    for event in TIMELINE_EVENTS:
        if event.id == event_id:
            return event
    # If not found, raise 404
    raise HTTPException(status_code=404, detail="Timeline event not found")

    

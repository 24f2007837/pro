from collections import defaultdict
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Assigned values
ASSIGNED_API_KEY = "ak_j0kyu571rwfdtwy7vtp35btk"
USER_EMAIL = "24f2007837@ds.study.iitm.ac.in"

# Enable CORS for browser verification
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Event(BaseModel):
    user: str
    amount: float
    ts: int

class AnalyticsRequest(BaseModel):
    events: List[Event]

@app.post("/analytics")
def compute_analytics(
    payload: AnalyticsRequest, 
    x_api_key: str = Header(None, alias="X-API-Key")
):
    # Validate API Key
    if not x_api_key or x_api_key != ASSIGNED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    
    events = payload.events
    total_events = len(events)
    
    # Track unique users
    users_set = {e.user for e in events}
    unique_users = len(users_set)
    
    # Calculate revenue (amount > 0 only) and aggregate per user for top_user
    total_revenue = 0.0
    user_positive_totals = defaultdict(float)
    
    for e in events:
        if e.amount > 0:
            total_revenue += e.amount
            user_positive_totals[e.user] += e.amount

    # Determine top_user (user with highest positive-amount total; grader ensures no ties)
    top_user = ""
    if user_positive_totals:
        top_user = max(user_positive_totals, key=user_positive_totals.get)

    return {
        "email": USER_EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": round(total_revenue, 4),
        "top_user": top_user
    }

from collections import defaultdict
from fastapi import FastAPI, Header, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

ASSIGNED_API_KEY = "ak_j0kyu571rwfdtwy7vtp35btk"
USER_EMAIL = "24f2007837@ds.study.iitm.ac.in"

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
    response: Response,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    # Strict 401 for missing or incorrect API key
    if not x_api_key or x_api_key != ASSIGNED_API_KEY:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": "Unauthorized"}
    
    events = payload.events
    total_events = len(events)
    
    users_set = {e.user for e in events}
    unique_users = len(users_set)
    
    total_revenue = 0.0
    user_positive_totals = defaultdict(float)
    
    for e in events:
        if e.amount > 0:
            total_revenue += e.amount
            user_positive_totals[e.user] += e.amount

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

from fastapi import APIRouter;
from schemas import Session, DB_SERVICE_URL
import requests

router = APIRouter()

@router.get("/sessions", tags=["sessions"])
def read_sessions():
    response = requests.get(f"{DB_SERVICE_URL}/sessions")
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to fetch sessions"}
    return response.json()

@router.get("/sessions/{session_id}", tags=["sessions"])
def read_session(session_id: int): # Gets session matching the given session_id
    response = requests.get(f"{DB_SERVICE_URL}/sessions/{session_id}")
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to fetch requested session."}
    return response.json()

@router.post("/sessions", tags=["sessions"])
def create_session(session: Session):
    response = requests.post(f"{DB_SERVICE_URL}/sessions", json=session.model_dump())
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to create session."}
    return response.json()

@router.patch("/sessions/{session_id}", tags=["sessions"])
def update_session(session_id: int, new_session_data: dict):
    response = requests.patch(f"{DB_SERVICE_URL}/sessions/{session_id}", json=new_session_data)
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to update session."}
    return response.json()

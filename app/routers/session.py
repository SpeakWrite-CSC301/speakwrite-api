from fastapi import APIRouter, Depends, Query;
from schemas import Session, DB_SERVICE_URL
import requests
from typing import Optional
from .user import get_current_user

router = APIRouter()

@router.get("/sessions", tags=["sessions"])
def read_sessions(current_user: int = Depends(get_current_user)): # Gets all sessions
    response = None
    if current_user:
        response = requests.get(f"{DB_SERVICE_URL}/sessions?user_id={current_user}")
    else:
        response = requests.get(f"{DB_SERVICE_URL}/sessions")
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to fetch sessions"}
    return response.json()

@router.get("/sessions/{session_id}", tags=["sessions"])
def read_session(session_id: int, current_user: int = Depends(get_current_user)): # Gets session matching the given session_id
    response = None
    if current_user:
        response = requests.get(f"{DB_SERVICE_URL}/sessions/{session_id}?user_id={current_user}")
    else:
        response = requests.get(f"{DB_SERVICE_URL}/sessions/{session_id}")
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to fetch requested session."}
    return response.json()

@router.post("/sessions", tags=["sessions"])
def create_session(session: Session, current_user: int = Depends(get_current_user)):
    response = requests.post(f"{DB_SERVICE_URL}/sessions?user_id={current_user}", json=session.model_dump())
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to create session."}
    return response.json()

@router.patch("/sessions/{session_id}", tags=["sessions"])
def update_session(session_id: int, new_session_data: dict, current_user: int = Depends(get_current_user)):
    response = None
    if current_user:
        response = requests.patch(f"{DB_SERVICE_URL}/sessions/{session_id}?user_id={current_user}", json=new_session_data)
    else:   
        response = requests.patch(f"{DB_SERVICE_URL}/sessions/{session_id}", json=new_session_data)
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to update session."}
    return response.json()

@router.delete("/sessions/{session_id}", tags=["sessions"])
def delete_session(session_id: int, current_user: int = Depends(get_current_user)):
    response = None
    if current_user:
        response = requests.delete(f"{DB_SERVICE_URL}/sessions/{session_id}?user_id={current_user}")
    else:
        response = requests.delete(f"{DB_SERVICE_URL}/sessions/{session_id}")
    if response.status_code != 200:
       return {"error": "DB SERVICE ERROR: Failed to delete session."}
    return response.json()

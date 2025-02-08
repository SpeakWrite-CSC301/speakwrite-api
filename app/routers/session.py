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

@router.post("/sessions", tags=["sessions"])
def create_session(session: Session):
    response = requests.post(f"{DB_SERVICE_URL}/sessions", json=session.model_dump())
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to create session."}
    return response.json()

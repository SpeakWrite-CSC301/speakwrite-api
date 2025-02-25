from fastapi import APIRouter
from schemas import User, DB_SERVICE_URL
import requests

router = APIRouter()

@router.get("/users", tags=["users"])
def read_users():
    response = requests.get(f"{DB_SERVICE_URL}/users")
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to fetch users"}
    return response.json()

@router.post("/users", tags=["users"])
def create_user(user: User):
    response = requests.post(f"{DB_SERVICE_URL}/users", json=user.model_dump())
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to create user"}
    return response.json()

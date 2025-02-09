from fastapi import APIRouter;
from schemas import Chat, DB_SERVICE_URL
import requests

router = APIRouter()

@router.get("/chats", tags=["chats"])
def read_chats():
    response = requests.get(f"{DB_SERVICE_URL}/chats")
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to fetch chats"}
    return response.json()

@router.post("/chats", tags=["chats"])
def create_chat(chat: Chat):
    response = requests.post(f"{DB_SERVICE_URL}/chats", json=chat.model_dump())
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to create chat"}
    return response.json()

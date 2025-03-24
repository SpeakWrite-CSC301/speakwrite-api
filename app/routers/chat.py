from fastapi import APIRouter, Depends;
from schemas import Chat, DB_SERVICE_URL
from .session import update_session
import requests
from .user import get_current_user 

router = APIRouter()

@router.get("/chats", tags=["chats"])
def read_chats(current_user: int = Depends(get_current_user)):
    response = requests.get(f"{DB_SERVICE_URL}/chats?user_id={current_user}")
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to fetch chats"}
    return response.json()

@router.post("/chats", tags=["chats"])
def create_chat(chat: Chat, current_user: int = Depends(get_current_user)):
    chat.sender = current_user
    response = requests.post(f"{DB_SERVICE_URL}/chats", json=chat.model_dump())
    if response.status_code != 200:
        return {"error": "DB SERVICE ERROR: Failed to create chat"}
    update_session(chat.session_id, {"message": chat.message})
    return response.json()

from pydantic import BaseModel
from typing import Optional

DB_SERVICE_URL = "http://localhost:9000"

# Creating objects to be used int other
class User(BaseModel):
    user_id: Optional[int] = None
    username: str
    email: str
    password: str


class Session(BaseModel):
    session_id: Optional[int] = None
    session_name: str
    # user_id: int
    context: dict = {}

    # class Config:
    #     arbitrary_types_allowed = True

class Chat(BaseModel):
    chats_id: Optional[int] = None
    session_id: int
    sender: str
    message: str

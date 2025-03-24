from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import requests
import jwt
from datetime import datetime, timedelta
from schemas import User, DB_SERVICE_URL
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class LoginRequest(BaseModel):
    email: str
    password: str

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("sub")
    if user_id is None:
      raise HTTPException(status_code=401, detail="Invalid token")
    return int(user_id)
  except jwt.PyJWTError:
    raise HTTPException(status_code=401, detail="Could not validate credentials")
  
def create_access_token(data: dict, expires_delta: timedelta = None):
  to_encode = data.copy()
  expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# @router.get("/users", tags=["users"])
# def read_users(current_user: int = Depends(get_current_user)):
#   response = requests.get(f"{DB_SERVICE_URL}/users")
#   if response.status_code != 200:
#     return {"error": "DB SERVICE ERROR: Failed to fetch users"}
#   return response.json()

@router.post("/auth/signup", tags=["users"])
def create_user(user: User):
  response = requests.post(f"{DB_SERVICE_URL}/users", json=user.model_dump())
  if response.status_code != 200:
    return {"error": "DB SERVICE ERROR: Failed to create user"}
  user_data = response.json()
  access_token = create_access_token(data={"sub": str(user_data["id"])}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
  print(access_token)
  return {"access_token": access_token, "user_id": user_data["id"], "token_type": "bearer"}

@router.post("/auth/login", tags=["auth"])
def login(form_data: LoginRequest):
  print(form_data)
  response = requests.post(
    f"{DB_SERVICE_URL}/auth/login",
    json={"email": form_data.email, "password": form_data.password}
  )
  if response.status_code != 200:
    raise HTTPException(status_code=400, detail="Incorrect email or password")
  user_data = response.json()
  access_token = create_access_token(data={"sub": str(user_data["id"])}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
  print(access_token)
  return {"access_token": access_token, "user_id": user_data["id"], "token_type": "bearer"}
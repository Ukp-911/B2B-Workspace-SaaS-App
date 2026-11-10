from fastapi import APIRouter,Depends
from .schemas import User_response
from src.auth.auth import get_current_user
from src.database.models import Users

app_routes=APIRouter()

@app_routes.get("/current_user",response_model=User_response)
def current_user(user:Users=Depends(get_current_user)): 
    return user
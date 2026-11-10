from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from src.database.connections import get_db
from src.Users.schemas import Usercreate
from src.Users.schemas import Register_response,refresh_request,Refresh_response
from src.database.models import Users
from .auth import hash_pswd,verify_pswd
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.auth import create_token,verify_refresh

auth_routes=APIRouter()

@auth_routes.post("/register",response_model=Register_response)
def register_user(user_detail:Usercreate,db:Session=Depends(get_db)):
    existing_user=db.query(Users).filter(Users.email==user_detail.email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="email already exists"
        )
    else:
        new_user=Users(
            username=user_detail.username,
            email=user_detail.email,
            password=hash_pswd(user_detail.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "message":"user created",
            "user":new_user
        }

@auth_routes.post("/login")
def login(login_detail:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(Users).filter(login_detail.username==Users.email).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail={
                "message":"invalid credentials"
            }
        )
    else:
        if not verify_pswd(login_detail.password,user.password):
            raise HTTPException(
                status_code=401,
                detail={
                    "message":"invalid credentials"
                }
            )
        access_token_creation_details={
            "uid":str(user.uid),
            "username":user.username,
            "email": user.email,
            "token_type":"access"
        }
        refresh_token_creation_details={
            "uid":str(user.uid),
            "username":user.username,
            "email": user.email,
            "token_type":"refresh"
        }
        access_token=create_token(access_token_creation_details)
        refresh_token=create_token(refresh_token_creation_details)
        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":"bearer"
        }

@auth_routes.post("/refresh", response_model=Refresh_response)
def refresh(refresh_tok:refresh_request,db:Session=Depends(get_db)):
    return {
        "status":"Success",
        "token":verify_refresh(refresh_tok.tok,db)
    }

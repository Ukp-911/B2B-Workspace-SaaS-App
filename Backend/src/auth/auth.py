from datetime import timedelta,timezone,datetime
from jose import jwt,JWTError
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,Header
from sqlalchemy.orm import Session
from src.database.connections import get_db
from src.database.models import Users,Membership
from src.config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES,REFRESH_TOKEN_EXPIRE_DAYS
from uuid import UUID

secret_key=SECRET_KEY
algorithm=ALGORITHM
access_token_expire=ACCESS_TOKEN_EXPIRE_MINUTES
refresh_token_expire=REFRESH_TOKEN_EXPIRE_DAYS
pwd=PasswordHash.recommended()

scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_token(data:dict):
    payload=data.copy()
    if payload.get("token_type")=="access":
        expire=datetime.now(timezone.utc)+timedelta(minutes=access_token_expire)
    else:
        expire=datetime.now(timezone.utc)+timedelta(days=refresh_token_expire)
    payload.update({
        "exp":expire
    })
    token=jwt.encode(payload,secret_key,algorithm=algorithm)
    return token    

def hash_pswd(pswd:str):
    return pwd.hash(pswd)

def verify_pswd(pswd,hashed_pswd):
    return pwd.verify(pswd,hashed_pswd)

def verify_token(tok:str=Depends(scheme)):
    try:
        token=jwt.decode(tok,secret_key,algorithms=algorithm)
    except JWTError:
        raise HTTPException(
            status_code=404,
            detail={
                "msg":"invalid token"
            }
        )
    if token.get("token_type")!="access":
        raise HTTPException(
            status_code=401,
            detail={
                "message":"wrong token type"
            }
        )
    return token

def get_current_user(token_data:dict=Depends(verify_token),db:Session=Depends(get_db)):
    user=db.query(Users).filter(Users.email==token_data.get("email")).first()
    if user is None:
        raise HTTPException(
            status_code=501,
            detail={
                "status":"User not found"
            }
        )
    else:
        return user

def verify_refresh(refresh_token:str,db:Session):
    try:
        data=jwt.decode(refresh_token,secret_key,algorithms=algorithm)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={
                "message":"invalid token"
            }
        )
    if data.get("token_type")!="refresh":
        raise HTTPException(
            status_code=401,
            detail={
                "message":"invalid token type"
            }
        )
    user=db.query(Users).filter(Users.email==data.get("email")).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message":"user not found"
            }
        )
    payload_new_access_token={
        "uid": str(user.uid),
        "username": user.username,
        "email": user.email,
        "token_type": "access",
    }
    return create_token(payload_new_access_token)

Role_Permissions={
    "admin":["create","edit","delete","view"],
    "member":["create","edit","view"],
    "viewer":["view"]
}

class AuthUser:
    def __init__(self,user:Users,org_id:UUID,role:str):
        self.user=user
        self.org_id=org_id
        self.role=role

    def has_permission(self,permission:str):
        if permission in Role_Permissions.get(self.role):
            return True
        else:
            raise HTTPException(
                status_code=403,
                detail={
                    "message":"dont have this permission"
                }
            )

def get_auth_user(user:Users=Depends(get_current_user),org_id:UUID=Header(...),db:Session=Depends(get_db)):
    m=db.query(Membership).filter(Membership.user_id==user.uid, Membership.org_id==org_id).first()
    if m!=None:
        return AuthUser(user,org_id,m.role)
    else:
        raise HTTPException(
            status_code=403,
            detail={
                "message":"not a member"
            }
        )

def require_create(authuser:AuthUser=Depends(get_auth_user)):
    authuser.has_permission("create")
    return authuser

def require_view(authuser:AuthUser=Depends(get_auth_user)):
    authuser.has_permission("view")
    return authuser

def require_delete(authuser:AuthUser=Depends(get_auth_user)):
    authuser.has_permission("delete")
    return authuser

def require_edit(authuser:AuthUser=Depends(get_auth_user)):
    authuser.has_permission("edit")
    return authuser


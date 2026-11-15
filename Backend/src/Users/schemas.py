from pydantic import BaseModel,ConfigDict,Field
from uuid import UUID
class Usercreate(BaseModel):
    username:str
    email:str
    password:str

class User_response(BaseModel):
    uid:UUID
    username:str
    email:str
    
    model_config=ConfigDict(from_attributes=True)

class Register_response(BaseModel):
    message:str
    user:User_response

class refresh_request(BaseModel):
    tok:str

class Refresh_response(BaseModel):
    status:str
    token:str

class UpdateUsername(BaseModel):
    username:str = Field(min_length=3, max_length=30)

class ResponseUsernameUpdate(BaseModel):
    msg:str
    new_username:UpdateUsername

class New_pswd(BaseModel):
    new_pswd=str=Field(min_length=8, max_length=128)
    old_pswd=str
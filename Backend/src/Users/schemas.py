from pydantic import BaseModel,ConfigDict
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
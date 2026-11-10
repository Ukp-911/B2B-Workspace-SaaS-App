from sqlalchemy import Column,String,Boolean,Uuid,ForeignKey,UniqueConstraint,func
from src.database.connections import Base
import uuid

class Users(Base):
    __tablename__="users"
    uid = Column(Uuid,primary_key=True,nullable=False,default=uuid.uuid4)
    username=Column(String,nullable=False)
    email=Column(String,unique=True,nullable=False)
    password=Column(String,nullable=False)
    role=Column(String,default="user",nullable=False)
    is_verified=Column(Boolean,default=False)

class Organisation(Base):
    __tablename__="organisation"
    org_id= Column(Uuid, primary_key=True, nullable=False, default=uuid.uuid4)
    name=Column(String,nullable=False)
    created_by=Column(Uuid, ForeignKey("users.uid"),nullable=False) 

class Membership(Base):
    __tablename__="membership"
    __table_args__= (UniqueConstraint("user_id","org_id"),)
    mem_id=Column(Uuid,primary_key=True,nullable=False,default=uuid.uuid4)
    user_id=Column(Uuid, ForeignKey("users.uid"),nullable=False)
    org_id=Column(Uuid,ForeignKey("organisation.org_id"),nullable=False)
    role=Column(String,nullable=False,default="viewer")

class Tasks(Base):
    __tablename__="tasks"
    id=Column(Uuid,primary_key=True, default=uuid.uuid4)
    org_id=Column(Uuid,ForeignKey("organisation.org_id"),index=True, nullable=False)
    task=Column(String,nullable=False)
    status=Column(String,nullable=False,default="todo")
    created_by=Column(Uuid,ForeignKey("users.uid"),nullable=False)
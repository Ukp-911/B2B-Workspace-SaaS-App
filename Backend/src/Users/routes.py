from fastapi import APIRouter,Depends,HTTPException
from .schemas import User_response
from src.auth.auth import get_current_user,verify_pswd,hash_pswd
from src.database.models import Users,Membership,Organisation,Tasks
from sqlalchemy.orm import Session
from src.database.connections import get_db
from src.Users.schemas import UpdateUsername,ResponseUsernameUpdate,New_pswd

app_routes=APIRouter()

@app_routes.get("/current_user",response_model=User_response)
def current_user(user:Users=Depends(get_current_user)): 
    return user

@app_routes.patch("/me", response_model=ResponseUsernameUpdate)
def update_username(updusername:UpdateUsername,user:Users=Depends(get_current_user),db:Session=Depends(get_db)):
    user=db.query(Users).filter(Users.email==user.email).first()
    user.username=updusername.username
    db.commit()
    db.refresh(user)
    return {
        "msg":"username updated",
        "new_username":user.username
    }

@app_routes.patch("/change_pswd")
def change_pswd(New_Pswd:New_pswd,user:Users=Depends(get_current_user),db:Session=Depends(get_db)):
    if not verify_pswd(New_Pswd.old_pswd,user.password):
        raise HTTPException(
            status_code=400,
            detail={
                "status":"fail",
                "message":"provided pswd was incorrect"
            }
        )
    else:
        user.password=hash_pswd(New_Pswd.new_pswd)
        db.commit()
        db.refresh(user)
        return {
            "message":"password changed successfully"
        }

@app_routes.delete("/delete_me")
def delete_own_account(user:Users=Depends(get_current_user),db:Session=Depends(get_db)):
    admin_mems=db.query(Membership).filter(Membership.user_id==user.uid,
    Membership.role=="admin" ).all()

    for i in admin_mems:
        other_admins=db.query(Membership).filter(
            Membership.role=="admin",
            Membership.org_id==i.org_id,
            Membership.user_id!=i.user_id
        ).first()
        if other_admins is None:
            org=db.query(Organisation).filter(Organisation.org_id==i.org_id).first()
            raise HTTPException(
                status_code=409,
                detail={
                    "message":f"you are only admin in {org.name}.Promote another admin first"
                }
            )

    db.query(Organisation).filter(Organisation.created_by==user.uid).update({Organisation.created_by:None})
    db.query(Membership).filter(Membership.user_id==user.uid).delete()
    db.query(Tasks).filter(Tasks.created_by==user.uid).update({Tasks.created_by:None})
    db.query(Users).filter(Users.uid==user.uid).delete()
    db.commit()


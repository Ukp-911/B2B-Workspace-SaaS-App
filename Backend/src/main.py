from fastapi import FastAPI
from src.database.connections import engine,Base
from src.auth.routes import auth_routes
from src.Users.routes import app_routes
app=FastAPI()

app.include_router(auth_routes,prefix="/auth")
app.include_router(app_routes,prefix="")

Base.metadata.create_all(bind=engine)
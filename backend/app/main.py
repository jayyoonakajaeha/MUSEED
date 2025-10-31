from fastapi import FastAPI
from .database import engine, Base
from . import models
from .routers import auth

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the MUSEED Backend!"}

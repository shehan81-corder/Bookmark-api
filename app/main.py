from fastapi import FastAPI
from app.db import models
from app.api import auth

app = FastAPI(title="Bookmarks API")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

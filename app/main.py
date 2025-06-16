# app/main.py
from fastapi import FastAPI
from app.routes import jobs

app = FastAPI()
app.include_router(jobs.router)

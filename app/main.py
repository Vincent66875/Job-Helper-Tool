# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import jobs

app = FastAPI()
app.include_router(jobs.router)
app.mount("/static", StaticFiles(directory="static"), name="static")
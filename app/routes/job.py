from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from app.db import crud

router = APIRouter()
@router.get("/jobs")
def list_jobs():
    return crud.get_all_job()

@router.post("/jobs")
def create_job(title: str = Form(...), company: str = Form(...), status: str = Form(...)):
    crud.create_job(title, company, status)
    return RedirectResponse(url="/", status_code=303)

@router.post("/jobs/delete/{job_id}")
def delete_job(job_id: str):
    return RedirectResponse(url="/", status_code=303)
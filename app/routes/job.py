from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import crud
from app.models.schemas import Job
templates = Jinja2Templates(directory="app/templates")
router = APIRouter()
dummy_user_id = "user_123"
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

@router.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(request: Request):
    jobs = get_jobs_by_user(dummy_user_id)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "jobs": jobs,
    })
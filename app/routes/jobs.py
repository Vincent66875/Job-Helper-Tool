# app/routes/job.py
from fastapi import APIRouter, Form, Request, Depends, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import crud
from app.models.schemas import Job
import fitz
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()
dummy_user_id = "user_123"
tokenizer = AutoTokenizer.from_pretrained("sentence-transformer/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

@router.get("/jobs")
def list_jobs():
    return crud.get_all_job()

@router.post("/jobs")
def create_job(title: str = Form(...), company: str = Form(...), status: str = Form(...)):
    crud.create_job(dummy_user_id, title, company, status)
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/jobs/delete/{job_id}")
def delete_job(job_id: str):
    crud.delete_job(dummy_user_id, job_id)
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/jobs/update/{job_id}")
def update_job(job_id: str, status: str = Form(...)):
    crud.update_job_status(dummy_user_id, job_id, status)
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(request: Request):
    jobs = crud.get_jobs_by_user(dummy_user_id)
    return templates.TemplateResponse("dashboard.html", {"request": request, "jobs": jobs})
    
@router.get("/jobs/{job_id}", response_class=HTMLResponse)
def job_detail(job_id: str, request: Request):
    job = crud.get_job_by_id(dummy_user_id, job_id)
    if not job:
        return HTMLResponse(content="Job not found", status_code=404)
    return templates.TemplateResponse("job_detail.html", {"request": request, "job": job})

@router.post("/jobs/update_description/{job_id}")
def update_job_description(job_id: str, description: str = Form(...)):
    crud.update_job_description(dummy_user_id, job_id, description)
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)

@router.post("/jobs/upload_resume/{job_id}")
async def upload_resume(job_id: str, resume: UploadFile = File(...)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{job_id}_{resume.filename}")
    with open(file_path, "wb") as f:
        f.write(await resume.read())
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)

def extract_resume_text(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text
# term frequency inverse Doc frequency
def compute_similarity(text1, text2):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform([text1, text2])
    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[0:2])
    return sim[0][0]
#convert text to embeding
def embed(text):
    imputs = tokenizer(text, return_tensors = "pt", padding = True, truncation = True)
    with torch.no_grad():
        outputs = model(**input)
    return outputs.last_hidden_state.mean(dim=1)
def compute_bert_similarity(text1, text2):
    embed1 = embed(text1)
    embed2 = embed(text2)
    return torch.nn.functional.cosine_similarity(embed1, embed2)
    
# app/routes/job.py
from fastapi import APIRouter, Form, Request, Depends, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import crud
from app.models.schemas import Job
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from transformers import AutoTokenizer, AutoModel
from keybert import KeyBERT
import torch
import fitz
import os
import spacy

nlp = spacy.load("en_core_web_lg")
templates = Jinja2Templates(directory="app/templates")
router = APIRouter()
dummy_user_id = "user_123"
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
kw_model = KeyBERT()

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
    job_description = job.get("description", "")
    if not job:
        return HTMLResponse(content="Job not found", status_code=404)
    
    #locate resume
    upload_dir = "uploads"
    resume_file = None
    for filename in os.listdir(upload_dir):
        if filename.startswith(job_id + "_"):
            resume_file = os.path.join(upload_dir, filename)
            break
    resume_text = ""
    missing_kw = []
    score = None
    print("Print out")
    if resume_file:
        resume_text = extract_resume_text(resume_file)
        missing_kw = missing_keywords(job_description, resume_text)
        score = compute_bert_similarity(job_description, resume_text).item()
    score = f"{score * 100:.2f}%"

    return templates.TemplateResponse("job_detail.html", {
        "request": request,
        "job": job,
        "resume_text": resume_text,
        "missing_keywords": missing_kw,
        "score": score,
    })

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

#resume analysis
def extract_resume_text(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text
def extract_keywords(text):
    doc = nlp(text)
    keywords = []

    for ent in doc.ents:
        cleaned = ent.text.strip().lower()
        if ent.label_ not in {"ORG"}:
            keywords.append(cleaned)
            print(f"{cleaned} ({ent.label_})")
    return sorted(set(keywords))

def missing_keywords(job_description, resume_text) -> List[str]:
    job_keywords = extract_keywords(job_description)
    resume_lower = resume_text.lower()
    return [kw for kw in job_keywords if kw not in resume_lower]

#convert text to embeding
def embed(text):
    inputs = tokenizer(text, return_tensors = "pt", padding = True, truncation = True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)
def compute_bert_similarity(text1, text2):
    embed1 = embed(text1)
    embed2 = embed(text2)
    return torch.nn.functional.cosine_similarity(embed1, embed2)
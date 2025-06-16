from .database import users_table
from .database import jobs_table
from app.models.schemas import Job, User
import uuid
from datetime import datetime

def create_job(title: str, company: str, status: str) -> Job:
    job_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    job_data = {
        "job_id": job_id,
        "title": title,
        "company": company,
        "status": status,
        "created_at": created_at
    }
    jobs_table.put_item(Item=job_data)
    return Job(**job_data)

def get_all_job():
    response = jobs_table.scan()
    items = response.get("Item", [])
    return [Job(**item) for item in items]

def delete_job(job_id: str):
    jobs_table.delete_item(Key={"job_id": job_id})

from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class Job(BaseModel):
    job_id: str
    user_id: str
    title: str
    company: str
    status: Literal["Applied", "Interviewing", "Offer", "Rejected"]
    created_at: str
class User(BaseModel):
    user_id: str
    name: str
    email: str
    password: str
    created_at: str

#app/db/crud.py
from .database import users_table
from .database import jobs_table
from app.models.schemas import Job, User
from boto3.dynamodb.conditions import Key
from mypy_boto3_dynamodb.service_resource import Table
import uuid
from datetime import datetime

def create_job(user_id: str, title: str, company: str, status: str) -> Job:
    job_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    job_data = {
        "user_id": user_id,
        "job_id": job_id,
        "title": title,
        "company": company,
        "status": status,
        "created_at": created_at,
        "description": ""
    }
    jobs_table.put_item(Item=job_data)
    return Job(**job_data)

def get_all_job():
    response = jobs_table.scan()
    items = response.get("Items", [])
    return [Job(**item) for item in items]
def get_jobs_by_user(user_id: str):
    response = jobs_table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    )
    items = response.get("Items", [])
    return [Job(**item) for item in items]
def get_job_by_id(user_id, job_id):
    response = jobs_table.get_item(
        Key={'user_id': user_id, 'job_id': job_id}
    )
    return response.get("Item")

def delete_job(user_id: str, job_id: str):
    jobs_table.delete_item(Key={"user_id": user_id, "job_id": job_id})


def update_job_status(user_id: str, job_id: str, new_status: str):
    jobs_table.update_item(
        Key={"user_id": user_id, "job_id": job_id},
        UpdateExpression="SET #s = :new_status",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":new_status": new_status}
    )
def update_job_description(user_id: str, job_id: str, description: str):
    jobs_table.update_item(
        Key={'user_id': user_id, 'job_id': job_id},
        UpdateExpression="SET description = :desc",
        ExpressionAttributeValues={":desc": description}
    )
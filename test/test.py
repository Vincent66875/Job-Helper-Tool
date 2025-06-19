from app.db.database import jobs_table
from boto3.dynamodb.conditions import Key

anw = jobs_table.query(
    KeyConditionExpression=Key("user_id").eq("user_123")
)
print(anw)
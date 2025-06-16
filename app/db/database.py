import boto3
import os
from dotenv import load_dotenv
load_dotenv()

dynamodb = boto3.resource(
    'dynamodb',
    region_name = os.getenv('us-east-1'),
    aws_access_key_id = os.getenv('AKIASIVGLDS4HB3J5QVV'),
    aws_secret_access_key = os.getenv('APqSe52/WIo9wLyoR1CkTl1mpvU04anoN8ah051U4')
)
users_table = dynamodb.Table("users")
jobs_table = dynamodb.Table("jobs")
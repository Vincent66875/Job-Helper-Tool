from app.db.database import job_table

def test_dynamo():
    print("Scanning table...")
    response = job_table.scan()
    print("Items:", response.get("Items", []))

test_dynamo()
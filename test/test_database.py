# test/test_database.py

import os
import pytest
from app.db import database

def test_dynamodb_connection():
    # Just check that the table resource objects exist
    assert database.dynamodb is not None, "DynamoDB resource is not initialized"
    assert database.jobs_table is not None, "jobs_table is not initialized"
    assert database.users_table is not None, "users_table is not initialized"

def test_jobs_table_name():
    assert database.jobs_table.name == "jobs", f"Expected table name 'jobs', got '{database.jobs_table.name}'"

def test_users_table_name():
    assert database.users_table.name == "users", f"Expected table name 'users', got '{database.users_table.name}'"

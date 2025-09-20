# app/api/v1/setup.py

import os
from fastapi import APIRouter, HTTPException, status
from app.database import execute

router = APIRouter(prefix="/setup", tags=["Setup"])

@router.post("/tables", status_code=status.HTTP_201_CREATED)
async def create_tables_from_file():
    """
    Reads schema.sql and executes all SQL commands to create tables.
    Accessible without authentication.
    """
    sql_file_path = os.path.join(os.path.dirname(__file__), "../../../sql/schema.sql")

    if not os.path.exists(sql_file_path):
        raise HTTPException(
            status_code=404,
            detail=f"SQL file not found at: {sql_file_path}"
        )

    try:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_commands = f.read()

        # Execute the entire file content
        await execute(sql_commands)

        return {
            "message": "Tables created successfully from schema.sql!",
            "file": sql_file_path,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute SQL file: {str(e)}"
        )

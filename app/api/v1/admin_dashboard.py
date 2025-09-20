from fastapi import APIRouter, Depends, Form, HTTPException
from app.core.security import require_role
from app.database import execute_returning, fetch_one, fetch_all

router = APIRouter(prefix="/dashboard", tags=["Admin_Dashboard"])

@router.get("/admin/summary")
async def admin_dashboard(current_user=Depends(require_role("ADMIN"))):
    stats = {}

    stats["total_users"] = await fetch_one("SELECT COUNT(*) FROM users")
    stats["active_field_workers"] = await fetch_one("SELECT COUNT(*) FROM users WHERE role = 'FIELD_WORKER' AND is_active = TRUE AND is_approved = TRUE")
    stats["pending_approvals"] = await fetch_one("SELECT COUNT(*) FROM users WHERE role = 'FIELD_WORKER' AND is_approved = FALSE")
    stats["tasks_by_status"] = await fetch_all("""
        SELECT status, COUNT(*) FROM service_requests GROUP BY status
    """)

    return stats

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from app.core.security import require_role
from app.database import fetch_one, execute_returning

@router.put("/field-worker/{user_id}/approval")
async def approve_or_reject_field_worker(
    user_id: int,
    approve: bool,
    current_user=Depends(require_role("ADMIN"))
):
    """
    Admin can approve or reject a field worker.
    - approve=True → Approve
    - approve=False → Reject
    """
    # Check if user exists and is a field worker
    user = await fetch_one("SELECT * FROM users WHERE id = $1 AND role = 'FIELD_WORKER'", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Field worker not found")

    # Update approval status
    updated_user = await execute_returning(
        "UPDATE users SET is_approved = $1 WHERE id = $2 RETURNING *",
        approve, user_id
    )
    if not updated_user:
        raise HTTPException(status_code=500, detail="Failed to update approval status")


    action = "approved" if approve else "rejected"
    return {
        "message": f"Field worker {action}",
        "user_id": updated_user["id"],  # <-- include user ID
        "user": dict(updated_user)
    }

@router.put("/assign-task")
async def assign_task_to_worker(
    task_id: int,
    field_worker_id: int,
    current_user=Depends(require_role("ADMIN"))
):
    # 1. Check if task exists
    task = await fetch_one("SELECT * FROM service_requests WHERE id = $1", task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. Check if field worker exists and is approved & active
    worker = await fetch_one("SELECT * FROM users WHERE id = $1 AND role='FIELD_WORKER' AND is_active=TRUE AND is_approved=TRUE", field_worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Field worker not found or not approved/active")

    # 3. Assign task
    updated_task = await execute_returning(
        """
        UPDATE service_requests
        SET field_worker_id = $1, status = 'ASSIGNED', updated_at = $2
        WHERE id = $3
        RETURNING *
        """,
        field_worker_id, datetime.utcnow(), task_id
    )

    if not updated_task:
        raise HTTPException(status_code=500, detail="Failed to assign task")

    return {
        "message": f"Task {task_id} assigned to field worker {field_worker_id}",
        "task": dict(updated_task)
    }

@router.patch("/update-task-status/{task_id}")
async def admin_update_task_status(
    task_id: int,
    status: str = Form(...),
    current_user=Depends(require_role("ADMIN"))
):
    """
    Admin can update any task status. Simple success-only response.
    """
    # Fetch task
    task = await fetch_one("SELECT * FROM service_requests WHERE id = $1", task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Validate status
    valid_statuses = ["PENDING", "ASSIGNED", "IN_PROGRESS", "COMPLETED"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    # Update status
    completed_at = datetime.utcnow() if status == "COMPLETED" else None
    await execute_returning(
        """
        UPDATE service_requests
        SET status=$1, updated_at=$2, completed_at=$3
        WHERE id=$4
        """,
        status, datetime.utcnow(), completed_at, task_id
    )

    return {"message": "Task status updated successfully"}

import os
from passlib.context import CryptContext
from app.database import execute

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_default_admin():
    admin_email = os.getenv("ADMIN_EMAIL", "admin@fieldops.com")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    hashed_password = pwd_context.hash(admin_password)

    query = """
        INSERT INTO users (username, email, hashed_password, role, is_active, is_approved)
        VALUES ($1, $2, $3, 'ADMIN', TRUE, TRUE)
        ON CONFLICT (username) DO NOTHING
    """
    await execute(query, admin_username, admin_email, hashed_password)
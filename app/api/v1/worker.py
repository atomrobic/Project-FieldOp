

from datetime import datetime, timezone
from asyncpg import UniqueViolationError
from fastapi import APIRouter, Depends, File, HTTPException, status
from app.schemas.task import ServiceRequestOut, ServiceRequestCreate, ServiceRequestStatusUpdate, TaskProofOut
from app.core.security import get_password_hash, require_role
from app.database import execute_returning, fetch_all, fetch_one
from app.schemas.user import UserCreate

router = APIRouter(prefix="/tasks", tags=["field_operations"])


from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile
from typing import List, Optional
from datetime import datetime
from app.core.security import require_any_role
from app.database import fetch_one, fetch_all, execute_returning
from app.schemas.task import ServiceRequestOut, ServiceRequestStatusUpdate, TaskProofOut


@router.patch("/{task_id}/status", response_model=ServiceRequestOut)

async def update_task_status(
    task_id: int,
    status_update: ServiceRequestStatusUpdate = Depends(),
    notes: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    current_user=Depends(require_any_role("FIELD_WORKER", "ADMIN"))
):
    """
    - Field Worker: Update status of assigned tasks and optionally upload proofs.
    - Admin: Update status of any task.
    """
    # 1. Fetch task
    task = await fetch_one("SELECT * FROM service_requests WHERE id = $1", task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task = dict(task)

    # 2. Permission check
    if current_user["role"] == "FIELD_WORKER" and task["field_worker_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Task not assigned to you")

    # 3. Validate status transition
    valid_transitions = {
        "PENDING": ["ASSIGNED", "IN_PROGRESS"],
        "ASSIGNED": ["IN_PROGRESS"],
        "IN_PROGRESS": ["COMPLETED"],
        "COMPLETED": []
    }
    if status_update.status not in valid_transitions.get(task["status"], []):
        raise HTTPException(status_code=400, detail=f"Invalid status transition from {task['status']} to {status_update.status}")

    # 4. Update task status
    now = datetime.utcnow()
    completed_at = now if status_update.status == "COMPLETED" else None
    updated_task = await execute_returning(
        "UPDATE service_requests SET status=$1, updated_at=$2, completed_at=$3 WHERE id=$4 RETURNING *",
        status_update.status, now, completed_at, task_id
    )
    updated_task = dict(updated_task)

    # 5. Save proofs if provided
    if files:
        for file in files:
            file_location = f"uploads/{file.filename}"
            with open(file_location, "wb") as f:
                f.write(await file.read())
            await execute_returning(
                "INSERT INTO task_proofs (task_id, image_path, notes) VALUES ($1, $2, $3)",
                task_id, file_location, notes
            )

    # 6. Fetch all proofs
    proofs_raw = await fetch_all("SELECT * FROM task_proofs WHERE task_id = $1", task_id)
    proofs = [TaskProofOut(**proof) for proof in proofs_raw]

    return {**updated_task, "proofs": proofs}


@router.get("/field-worker/summary")
async def field_worker_summary(current_user=Depends(require_role("FIELD_WORKER"))):
    """
    Fetch summary for the logged-in Field Worker:
    - Total assigned tasks
    - Pending tasks
    - In-progress tasks
    - Completed tasks
    """
    worker_id = current_user["id"]

    # Total assigned tasks
    total_record = await fetch_one(
        "SELECT COUNT(*) AS count FROM service_requests WHERE field_worker_id = $1", worker_id
    )
    total_tasks = total_record["count"] if total_record else 0

    # Tasks by status
    tasks_status_raw = await fetch_all(
    """
    SELECT status, COUNT(*) AS count 
    FROM service_requests 
    WHERE field_worker_id = $1 
    GROUP BY status
    """,
    worker_id
)
    tasks_by_status = {r["status"]: r["count"] for r in tasks_status_raw}
    return {
        "total_tasks": total_tasks,
        "tasks_by_status": tasks_by_status
    }                                                                                                                                       

@router.put("/update-profile")
async def update_field_worker_profile(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(None),
    current_user=Depends(require_role("FIELD_WORKER"))
):
    """
    Update profile of logged-in Field Worker.
    Any profile update requires admin re-approval (is_approved=False).
    """
    hashed_pw = get_password_hash(password) if password else None

    query = """
        UPDATE users
        SET username=$1, email=$2, 
            hashed_password=COALESCE($3, hashed_password),
            is_approved=FALSE
        WHERE id=$4
        RETURNING *
    """
    updated_user = await execute_returning(query, username, email, hashed_pw, current_user["id"])
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Profile updated successfully. Await admin approval."}
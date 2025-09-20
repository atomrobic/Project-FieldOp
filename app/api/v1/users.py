from fastapi import APIRouter, Depends, Form, HTTPException, status
from app.api.v1.utils import save_task
from app.schemas.task import ServiceRequestCreate, ServiceRequestOut
from app.schemas.user import UserOut, UserCreate, UserUpdate, AdminUserUpdate
from app.core.security import get_password_hash, require_role, get_current_user, require_any_role
from app.database import fetch_one, fetch_all, execute_returning

# ✅ DEFINE THE ROUTER HERE
router = APIRouter(prefix="/users", tags=["Users"])


@router.put("/update-profile")
async def update_field_worker_profile(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(None),
    current_user=Depends(require_role("FIELD_WORKER"))
):
    user_id = current_user["id"]

    # Hash password if provided
    hashed_password = get_password_hash(password) if password else None

    query = """
        UPDATE users
        SET username = $1,
            email = $2,
            hashed_password = COALESCE($3, hashed_password)
        WHERE id = $4
        RETURNING *
    """

    updated_user = await execute_returning(query, username, email, hashed_password, user_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Profile updated", "user": dict(updated_user)}
@router.post("/", response_model=ServiceRequestOut, status_code=status.HTTP_201_CREATED)
async def create_task(task: ServiceRequestCreate, current_user=Depends(require_role("USER"))):
    new_task = await save_task(
        user_id=current_user["id"],
        title=task.title,
        description=task.description,
        location=task.location,
        urgency=task.urgency
    )
    if not new_task:
        raise HTTPException(status_code=500, detail="Failed to create task")
    return new_task

@router.get("/summary")
async def user_dashboard_summary(current_user=Depends(require_role("USER"))):
    user_id = current_user["id"]

    # Total tasks submitted by the user
    total_tasks_record = await fetch_one("SELECT COUNT(*) AS count FROM service_requests WHERE user_id = $1", user_id)
    total_tasks = total_tasks_record["count"] if total_tasks_record else 0

    # Tasks grouped by status
    tasks_by_status_raw = await fetch_all("""
        SELECT status, COUNT(*) AS count
        FROM service_requests
        WHERE user_id = $1
        GROUP BY status
    """, user_id)

    tasks_by_status = [{"status": r["status"], "count": r["count"]} for r in tasks_by_status_raw]

    return {
        "total_tasks": total_tasks,
        "tasks_by_status": tasks_by_status
    }
    
    
    
@router.patch("/rate/{task_id}")
async def rate_completed_service(
    task_id: int,
    rating: int = Form(..., ge=1, le=5),
    current_user=Depends(require_role("USER"))
):
    task = await fetch_one("SELECT * FROM service_requests WHERE id = $1 AND user_id = $2", task_id, current_user["id"])
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != "COMPLETED":
        raise HTTPException(status_code=400, detail="Cannot rate a task that is not completed")

    updated_task = await execute_returning(
        "UPDATE service_requests SET rating = $1 WHERE id = $2 RETURNING *",
        rating, task_id
    )
    return {"message": "Rating updated", "task": dict(updated_task)}
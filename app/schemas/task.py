from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Task Proof Models
# -------------------------
class TaskProofCreate(BaseModel):
    url: Optional[str] = None      # URL or image path
    notes: Optional[str] = None

class TaskProofOut(BaseModel):
    id: int
    task_id: int
    image_path: Optional[str]
    notes: Optional[str]
    uploaded_at: datetime

# -------------------------
# Service Request Base Models
# -------------------------
class ServiceRequestBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    urgency: str = "MEDIUM"

class ServiceRequestCreate(ServiceRequestBase):
    proofs: Optional[List[TaskProofCreate]] = []  # Optional proofs when creating a task

class ServiceRequestAssign(BaseModel):
    field_worker_id: int

class ServiceRequestStatusUpdate(BaseModel):
    status: str

class ServiceRequestRating(BaseModel):
    rating: int = Field(..., ge=1, le=5)

# -------------------------
# Service Request Output Model
# -------------------------
class ServiceRequestOut(ServiceRequestBase):
    id: int
    user_id: int
    field_worker_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    rating: Optional[int]
    proofs: List[TaskProofOut] = []

    class Config:
        from_attributes = True
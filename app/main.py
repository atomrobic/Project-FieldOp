from fastapi import FastAPI
from app.database import connect_db, disconnect_db
from app.api.v1 import admin_dashboard, auth, users, worker
from app.db_setup import setup  # 👈 Add this import


app = FastAPI(
    title="FieldOps - Field Service Coordination Platform",
    description="Backend API for managing field workers, tasks, and service requests with JWT auth and role-based access.",
    version="1.0.0",
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/user", tags=["Users"])
app.include_router(worker.router, prefix="/api/v1/tasks", tags=["field_operations"])
app.include_router(admin_dashboard.router, prefix="/api/v1/dashboard", tags=["Admin_Dashboard"])
app.include_router(setup.router, prefix="/api/v1/setup")  # 👈 Add this line

@app.on_event("startup")
async def startup():
    try:
        await connect_db()
        print("Database connected")
    except Exception as e:
        print("Failed to connect to DB:", e)

@app.on_event("shutdown")
async def shutdown():
    try:
        await disconnect_db()
        print("Database disconnected")
    except Exception as e:
        print("Failed to disconnect DB:", e)

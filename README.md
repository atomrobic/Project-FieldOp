🚀 FieldOps - FastAPI Backend

FieldOps is a field service coordination platform built using FastAPI.
It manages interactions between Users (Customers), Field Workers, and Admins.

The backend handles task creation, assignment, proof uploads, dashboard summaries, and role-based access control with JWT.

✨ Features
🔹 Authentication & Authorization

JWT-based authentication

Role-based access: USER, FIELD_WORKER, ADMIN

Secure password hashing with bcrypt

🔹 User (Customer)

Register & update profile

Create service requests (title, description, location, urgency)

Track service request status

Rate completed services

Fetch dashboard summary of their requests

🔹 Field Worker

Register & update profile (Admin approval required)

View assigned tasks

Update task status (Pending → In-progress → Completed)

Upload proofs (photos/notes) of task completion

Fetch dashboard summary of assigned/completed tasks

🔹 Admin

Approve/reject field workers

Activate/deactivate users

Assign tasks to field workers

Update any task status

Fetch overall dashboard summary (all users, tasks, workers)

🛠️ Tech Stack

FastAPI – Web framework

Asyncpg – PostgreSQL async driver

JWT (python-jose) – Authentication

Passlib (bcrypt) – Password hashing

Pydantic – Data validation
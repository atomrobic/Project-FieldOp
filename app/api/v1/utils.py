from app.database import execute_returning, fetch_one

async def save_task(user_id: int, title: str, description: str, location: str, urgency: str):
    """Create a new task for a user."""
    query = """
        INSERT INTO service_requests (user_id, title, description, location, urgency)
        VALUES ($1, $2, $3, $4, $5) RETURNING *
    """
    task = await execute_returning(query, user_id, title, description, location, urgency)
    if task:
        return dict(task)
    return None


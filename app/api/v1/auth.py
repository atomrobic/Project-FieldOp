from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserOut
from app.core.security import get_password_hash, create_access_token, verify_password
from app.database import fetch_one, execute_returning
from fastapi.security import OAuth2PasswordRequestForm  # 👈 ADD THIS LINE

router = APIRouter()
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException
from asyncpg.exceptions import UniqueViolationError

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    hashed_pw = get_password_hash(user.password)
    is_approved = False if user.role == "FIELD_WORKER" else True
    query = """
        INSERT INTO users (username, email, hashed_password, role, is_approved)
        VALUES ($1, $2, $3, $4, $5) RETURNING *
    """
    try:
        db_user = await execute_returning(
            query,
            user.username,
            user.email,
            hashed_pw,
            user.role,
            is_approved,
        )
        if not db_user:
            raise HTTPException(status_code=400, detail="Registration failed")

        # ✅ Convert Record -> dict
        db_user = dict(db_user)

        return db_user

    except UniqueViolationError as e:
        if "users_username_key" in str(e):
            detail = "Username already exists."
        elif "users_email_key" in str(e):
            detail = "Email already exists."
        else:
            detail = "Username or email already exists."
        raise HTTPException(status_code=409, detail=detail)
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await fetch_one("SELECT * FROM users WHERE username = $1", form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # convert Record → dict
    user = dict(user)

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="User deactivated")

    if user["role"] == "FIELD_WORKER" and not user["is_approved"]:
        raise HTTPException(status_code=403, detail="Field worker not approved")

    access_token = create_access_token(data={"sub": str(user["id"])})
    return {"access_token": access_token, "token_type": "bearer"}



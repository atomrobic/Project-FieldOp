from pydantic_settings import BaseSettings

class Settings(BaseSettings):
 DATABASE_URL: str = "postgresql://postgres:akhil@localhost:5432/my_db_pg"
 SECRET_KEY: str = "your_super_secret_key"  # change this to a strong random value!
 ALGORITHM: str = "HS256"
 ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

class Config:
        env_file = ".env"

settings = Settings()
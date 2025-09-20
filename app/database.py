import os
import asyncpg
from app.core.config import settings

pool = None

async def connect_db():
    global pool
    pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=5, max_size=20)

async def disconnect_db():
    await pool.close()

async def fetch_one(query, *args):
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def fetch_all(query, *args):
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)

async def execute(query, *args):
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)

async def execute_returning(query, *args):
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)
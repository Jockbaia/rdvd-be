from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import get_current_user
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/data", tags=["data"])

@router.get("/")
async def get_data(user: User = Depends(get_current_user)) -> dict[str, Any]:
    return user.data

@router.put("/")
async def update_data(
    payload: dict[str, Any],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    user.data = payload
    await db.commit()
    await db.refresh(user)
    return user.data

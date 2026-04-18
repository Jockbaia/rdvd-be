from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import get_current_user
from app.database import get_db
from app.models.radar import Radar
from app.models.user import User
from datetime import datetime
from pydantic import BaseModel
from app.schemas.radar import Battery

class RechargeRequest(BaseModel):
    recharge_time: datetime

router = APIRouter(prefix="/radar", tags=["radar"])

@router.get("/info")
async def get_radar_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Return the current user's radar battery info in a 'battery' wrapper."""
    radar_result = await db.execute(select(Radar).where(Radar.user_id == current_user.id))
    radar = radar_result.scalar_one_or_none()
    if not radar:
        raise HTTPException(status_code=404, detail="Radar not found")
    battery = Battery(
        last_charge=radar.last_charge, # type: ignore
        battery_capacity=radar.battery_capacity # type: ignore
    )
    return {"battery": battery.dict(by_alias=True)}

@router.post("/recharge", status_code=200)
async def recharge_battery(
    payload: RechargeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Recharge the user's radar battery."""
    recharge_time = payload.recharge_time
    radar_result = await db.execute(select(Radar).where(Radar.user_id == current_user.id))
    radar = radar_result.scalar_one_or_none()
    if not radar:
        raise HTTPException(status_code=404, detail="Radar not found")
    radar.last_charge = recharge_time # type: ignore
    db.add(radar)
    await db.commit()
    battery = Battery(
        last_charge=radar.last_charge, # type: ignore
        battery_capacity=radar.battery_capacity # type: ignore
    )
    return {"message": "Battery recharged", "battery": battery.dict(by_alias=True)}

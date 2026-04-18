from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.database import get_db
from app.models.user import User
from app.models.radar import Radar
from app.schemas.radar import Battery
from app.schemas.user import UserCreate
from datetime import datetime
from pydantic import BaseModel

class RechargeRequest(BaseModel):
    recharge_time: datetime

# Router Setup
router = APIRouter(prefix="/users", tags=["users"])

# User Authentication Endpoints
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """JWT token endpoint for user login."""
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", status_code=201)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user and create a radar entry."""
    result = await db.execute(
        select(User).where(User.username == payload.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        data={},
    )
    db.add(user)
    await db.flush()
    # TODO: Bind "battery_capacity" to a default value in the database or a config setting
    radar = Radar(user_id=user.id, last_charge=None, battery_capacity=3000)
    db.add(radar)
    await db.commit()
    return {"message": f"User created"}

@router.post("/login")
async def login(
    credentials: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Login endpoint for user authentication and battery info."""
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Fetch radar entry
    radar_result = await db.execute(
        select(Radar).where(Radar.user_id == user.id)
    )
    radar = radar_result.scalar_one_or_none()
    battery = None
    if radar:
        last_charge = radar.last_charge
        import datetime as pydt
        if last_charge is not None and not isinstance(last_charge, pydt.datetime):
            last_charge = None
        battery = Battery(
            last_charge=last_charge, # type: ignore
            battery_capacity=radar.battery_capacity # type: ignore
        )
    access_token = create_access_token(data={"sub": user.username})
    return {
        "message": "Login successful",
        "battery": battery.dict(by_alias=True) if battery else None,
        "jwt": {
            "access_token": access_token,
            "token_type": "bearer"
        }
    }

# Radar/Battery Endpoints
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
    return {"message": "Battery recharged", "lastCharge": recharge_time}

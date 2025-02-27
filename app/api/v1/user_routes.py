from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.core.database import get_db
from app.exceptions import UserAlreadyExistsException
from app.schemas import UserCreate, UserResponse
from app.services import UserService

user_router = APIRouter()


@user_router.post("/", status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        uid = await UserService.register_user(db, user)
        return {"user_id": uid}
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

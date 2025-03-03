from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_current_user_id
from app.exceptions import UserAlreadyExistsException, credentials_exception
from app.schemas import UserCreate, UserResponse
from app.services import UserService, AuthService

user_router = APIRouter()


@user_router.get("/me", response_model=UserResponse)
async def read_users_me(
        user_id: Annotated[int, Depends(get_current_user_id)],
        db: AsyncSession = Depends(get_db)
) -> UserResponse:
    user = await UserService(db=db).get_user(user_id=user_id)
    if user is None:
        raise credentials_exception
    return UserResponse.model_validate(user)


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user = await UserService(db=db).get_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        uid = await UserService(db=db).register_user(user=user, hasher=AuthService.hash_password)
        return {"user_id": uid}
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )

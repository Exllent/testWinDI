from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import AuthService
from app.schemas import LoginRequest

auth_router = APIRouter()


@auth_router.post("/token")
async def login_for_access_token(user: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.authenticate_user(db=db, user=user)
    # user = get_user_by_email(form_data.username)
    # if not user or not user.verify_password(form_data.password):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # access_token = create_access_token({"sub": user.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # refresh_token = create_refresh_token({"sub": user.email}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    #
    # return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# @router.post("/refresh")
# async def refresh_access_token(refresh_token: str):
#     email = verify_refresh_token(refresh_token)
#     if not email:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")
#
#     new_access_token = create_access_token({"sub": email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#
#     return {"access_token": new_access_token, "token_type": "bearer"}

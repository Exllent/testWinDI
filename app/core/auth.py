from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from starlette.websockets import WebSocket

from app.core import auth_config
from app.exceptions import credentials_exception

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    try:
        payload = jwt.decode(token, auth_config.secret_key, algorithms=[auth_config.algorithm])
        user_id = payload.get("uid")
        if not isinstance(user_id, int):
            raise credentials_exception
        return user_id
    except InvalidTokenError:
        raise credentials_exception


async def ws_get_current_user_id(websocket: WebSocket) -> int:
    token = websocket.headers.get('Authorization')
    if token is None:
        raise credentials_exception
    token = token.split("Bearer ")[-1]
    return await get_current_user_id(token=token)

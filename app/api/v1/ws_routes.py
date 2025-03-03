from typing import Annotated
from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import ws_get_current_user_id, get_db
from app.ws_manager import WebSocketManager
from app.repositories import ChatRepository
from app.services import WebSocketService
from app.exceptions import (
    CreateMessageException,
    CreateBalkMessageException,
    InternalServerErrorException
)

ws_router = APIRouter()
ws_manager = WebSocketManager()


@ws_router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
        chat_id: int,
        websocket: WebSocket,
        user_id: Annotated[int, Depends(ws_get_current_user_id)],
        db: AsyncSession = Depends(get_db)
):
    result = await ChatRepository(session=db).get_type_with_user_auth(chat_id=chat_id, user_id=user_id)
    print(result)
    print(user_id)
    if result is None:
        await websocket.close(code=1008)
        return

    await ws_manager.connect(chat_id=chat_id, user_id=user_id, websocket=websocket)
    while True:
        try:
            text = await websocket.receive_text()
            create_message_data = {"chat_id": chat_id, "sender_id": user_id, "text": text}
            msg_id = await WebSocketService(user_id, db).create_message(create_message_data, result.type)
            message_data = {"msg": text, "uid": user_id, "msg_id": msg_id}
            await ws_manager.send_to_others(chat_id=chat_id, message=message_data, websocket=websocket)
        except CreateMessageException:
            print('exception')
            continue

        except WebSocketDisconnect as e:
            ws_manager.disconnect(chat_id=chat_id, user_id=user_id, websocket=websocket)
            break

        except (WebSocketDisconnect, CreateBalkMessageException, InternalServerErrorException) as e:
            await websocket.close(code=e.status_code)
            ws_manager.disconnect(chat_id=chat_id, user_id=user_id, websocket=websocket)
            break

from fastapi import APIRouter, WebSocket, Depends
from app.ws_manager import WebSocketManager

ws_router = APIRouter()
ws_manager = WebSocketManager()

@ws_router.websocket("/ws/{user_id}")
async def websocket_endpoint(user_id: int, websocket: WebSocket):
    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.send_message(user_id, f"Echo: {data}")
    except Exception:
        pass
    finally:
        ws_manager.disconnect(user_id)

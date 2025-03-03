from collections import defaultdict

from fastapi import WebSocket


class WebSocketManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WebSocketManager, cls).__new__(cls)
            cls._instance.active_connections = defaultdict(lambda: defaultdict(list))
        return cls._instance

    # def __init__(self):
    #     self.active_connections: dict[int, dict[int, list[WebSocket]]] = defaultdict(lambda: defaultdict(list))

    async def connect(self, chat_id: int, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[chat_id][user_id].append(websocket)

    def disconnect(self, chat_id: int, user_id: int, websocket: WebSocket) -> None:
        if chat_id in self.active_connections and user_id in self.active_connections[chat_id]:
            self.active_connections[chat_id][user_id].remove(websocket)
            if not self.active_connections[chat_id][user_id]:
                del self.active_connections[chat_id][user_id]
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def notify_sender(self, chat_id: int, sender_id: int, message: dict) -> None:
        if chat_id not in self.active_connections:
            return
        for user_id, connections in self.active_connections[chat_id].items():
            if user_id == sender_id:
                for connection in connections:
                    await connection.send_json(message)

    async def broadcast_message(self, chat_id: int, message: dict) -> None:
        if chat_id not in self.active_connections:
            return
        for _, connections in self.active_connections[chat_id].items():
            for connection in connections:
                await connection.send_json(message)

    async def send_to_others(self, chat_id: int, message: dict, websocket: WebSocket) -> None:
        if chat_id not in self.active_connections:
            return
        for _, connections in self.active_connections[chat_id].items():
            for connection in connections:
                if connection != websocket:
                    await connection.send_json(message)

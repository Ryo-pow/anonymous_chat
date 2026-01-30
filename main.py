import datetime

# FastAPI本体とWebSocket関連
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Redis操作用（非同期版のredis-py）
import redis.asyncio as redis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # すべてのサイトからのアクセスを許可
    allow_methods=["*"],    # GETやPOSTなど、すべての命令を許可
    allow_headers=["*"],    # すべての設定項目を許可
)

#Redis接続(decode_responses=Trueにすると文字列として取得できます)
redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

active_connections: list[WebSocket] =[]

@app.websocket("/ws")
async def connections_websocket(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.post("/whisper")
async def create_whisper(message: str = ""):
    key = f"msg:{datetime.datetime.now().timestamp()}"
    await redis_client.set(key,message,ex = 3600)

    for connection in active_connections:
        await connection.send_text(f"新着メッセージ: {message}")
    return "保存と送信が完了しました"

@app.get("/whispers")
async def get_whispers():
    keys = await redis_client.keys("msg:*")
    message = []
    for key in keys:
        val = await redis_client.get(key)
        if val is not None:
            message.append(val)
    
    return {"active_whispers": message}

# 標準ライブラリ
import asyncio
import json
import time
import datetime

# FastAPI本体とWebSocket関連
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Redis操作用（非同期版のredis-py）
import redis.asyncio as redis

app = FastAPI()

#Redis接続(decode_responses=Trueにすると文字列として取得できます)
redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

@app.post("/whisper")
async def create_whisper(message: str = ""):
    key = f"msg:{datetime.datetime.now().timestamp()}"
    await redis_client.set(key,message,ex = 10)
    return f"保存しました!"

@app.get("/whispers")
async def get_whispers():
    keys = await redis_client.keys("msg:*")
    message = []
    for key in keys:
        val = await redis_client.get(key)
        if val is not None:
            message.append(val)
    
    return {"active_whispers": message}
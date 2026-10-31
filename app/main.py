import uvicorn
from fastapi import FastAPI
from app.core.redis import redis_client
from app.routes.upload_route import router as upload_route

app = FastAPI()
app.include_router(upload_route, prefix="/v1", tags=["chat v1"])


async def check_redis_connection():
    await redis_client.set("system_health", "Up, Working fine")
    value = await redis_client.get("system_health")
    print(value)

@app.get("/")
async def read_root():
    await check_redis_connection()
    return {"Hello": "World"}

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
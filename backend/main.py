from fastapi import FastAPI
from api.v1.api import api_router
from core.config import settings


app = FastAPI(title="Ragnarok Chaos Saga API", version="1.0.0")
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001)
    
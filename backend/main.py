from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.v1.api import api_router
from core.config import settings
import models.__all_models


app = FastAPI(title="Ragnarok Chaos Saga API", version="1.0.0")
app.include_router(api_router, prefix=settings.API_V1_STR)
# the game's images, for the management panel (management/): /assets/<path as stored in the database>
app.mount("/assets", StaticFiles(directory=Path(__file__).resolve().parent.parent / "assets"), name="assets")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001)
    
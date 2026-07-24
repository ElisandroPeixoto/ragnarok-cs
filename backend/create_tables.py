from core.config import DBBaseModel
from core.database import engine


async def create_tables() -> None:
    import models.__all_models
    print("Creating tables...")

    async with engine.begin() as conn:
        await conn.run_sync(DBBaseModel.metadata.create_all)
    

    print("Tables created successfully.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())

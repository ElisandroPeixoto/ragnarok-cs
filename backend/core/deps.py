from core.database import Session


async def get_session():
    async with Session() as session:
        yield session

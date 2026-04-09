from screenflix.core.database import get_session_maker


async def get_db_session():
    session_maker = get_session_maker()
    async with session_maker() as session:
        yield session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models import Base, User, Habit
from sqlalchemy import select
from config import DB_URL

engine = create_async_engine(DB_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# Инициализация таблиц при запуске
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Добавление пользователя (если еще нет)
async def get_or_create_user(telegram_id: int, username: str = None):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalars().first()

        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


# Добавление привычки
async def add_habit(telegram_id: int, title: str):
    async with async_session() as session:
        user = await get_or_create_user(telegram_id)
        new_habit = Habit(user_id=user.id, title=title)
        session.add(new_habit)
        await session.commit()


# Получение списка привычек пользователя
async def get_user_habits(telegram_id: int):
    async with async_session() as session:
        user = await get_or_create_user(telegram_id)
        result = await session.execute(select(Habit).where(Habit.user_id == user.id))
        return result.scalars().all()
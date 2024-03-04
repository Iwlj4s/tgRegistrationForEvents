from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Users, Events, Admins


# USERS #
async def orm_user_add_info(session: AsyncSession, data: dict, message):
    event_id = int(data['event_id'])

    async with session as async_session:
        result = await async_session.execute(select(Events).where(Events.id == event_id))
        event = result.scalar_one_or_none()
        event_name = event.event_name

    obj = Users(
        tg_id=message.from_user.id,
        event_id=event_id,
        name=data['user_name'],
        phone=int(data['user_phone']),
        email=data['user_email'],
        event=event_name
    )

    session.add(obj)

    await session.commit()


# Get user's tg_id #
async def orm_get_user_by_tg_id(session: AsyncSession, tg_id: int):
    query = select(Users).where(Users.tg_id == tg_id)
    result = await session.execute(query)
    user = result.scalar()
    return user


# EVENTS #
async def orm_get_events(session: AsyncSession):
    query = select(Events)
    result = await session.execute(query)
    return result.scalars().all()


# Get event id
async def orm_get_events_id(session: AsyncSession, event_id: int):
    query = select(Events).where(Events.id == event_id)
    result = await session.execute(query)
    event = result.scalar()
    return event


# ADMIN stuff #

# Get all users
async def orm_get_users(session: AsyncSession):
    query = select(Users)
    result = await session.execute(query)
    return result.scalars().all()


# Get one user
async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(Users).where(Users.id == user_id)
    result = await session.execute(query)

    return result.scalar()


# Change user's info
async def orm_change_user_info(session: AsyncSession, user_id: int, data):
    query = update(Users).where(Users.id == user_id).values(
        event_id=int(),
        name=data['user_name'],
        phone=int(data['user_phone']),
        email=data['user_email'],
        event=['event_id']
    )

    await session.execute(query)
    await session.commit()


# Delete User
async def orm_delete_user(session: AsyncSession, user_id: int):
    query = delete(Users).where(Users.id == user_id)
    await session.execute(query)
    await session.commit()

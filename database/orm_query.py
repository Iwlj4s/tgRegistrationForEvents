from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Users, Events, Admins, UsersEvents


# USERS #
async def orm_user_add_info(session: AsyncSession, data: dict, message):

    obj = Users(
        tg_id=message.from_user.id,
        name=data['user_name'],
        phone=int(data['user_phone']),
        email=data['user_email'],
    )

    session.add(obj)

    await session.commit()


# Update User #
async def orm_update_user(session: AsyncSession, user_id: int, data, message):

    query = update(Users).where(Users.id == user_id).values(
        tg_id=message.from_user.id,
        name=data['user_name'],
        phone=int(data['user_phone']),
        email=data['user_email'],)

    await session.execute(query)
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


# Save selected Event in UsersEvents
async def orm_save_user_event_info(session: AsyncSession, tg_id, event_id: int):
    # get event name #
    events = select(Events.event_name).where(Events.id == event_id)
    result = await session.execute(events)
    event_name = result.scalar()

    # get user info #
    user_tg_id = tg_id
    user_info = await orm_get_user_by_tg_id(session=session, tg_id=int(user_tg_id))

    # Add info in UsersEvents #
    user_event = UsersEvents(
        user_event_id=event_id,
        user_event_name=event_name,
        user_tg_id=user_info.tg_id,
        user_name=user_info.name,
        user_phone=user_info.phone,
        user_email=user_info.email
    )

    session.add(user_event)
    await session.commit()


async def orm_get_users_events_by_tg_id(session: AsyncSession, tg_id: int):
    query = select(UsersEvents).filter(UsersEvents.user_tg_id == tg_id)
    result = await session.execute(query)
    events = result.scalar()
    return events


async def orm_get_user_id_by_event_id(session: AsyncSession, event_id: int):
    query = select(UsersEvents).filter(UsersEvents.user_event_id == event_id)
    result = await session.execute(query)
    tg_id = result.scalar()
    return tg_id


# ADMIN stuff #

# Get all users
async def orm_get_users(session: AsyncSession):
    query = select(Users)
    result = await session.execute(query)
    return result.scalars().all()


# Get one user by id
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
    )

    await session.execute(query)
    await session.commit()


# Delete User
async def orm_delete_user(session: AsyncSession, user_id: int):
    query = delete(Users).where(Users.id == user_id)
    await session.execute(query)
    await session.commit()

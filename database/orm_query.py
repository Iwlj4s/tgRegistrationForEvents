from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Users


async def orm_user_add_info(session: AsyncSession, data: dict, message):
    obj = Users(
        tg_id=message.from_user.id,
        event_id=int(1),
        name=data['user_name'],
        phone=int(data['user_phone']),
        email=data['user_email'],
        event='One Event'
    )

    session.add(obj)

    await session.commit()


# Admin stuff #

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
        event=''
    )

    await session.execute(query)
    await session.commit()


# Delete User
async def orm_delete_user(session: AsyncSession, user_id: int):
    query = delete(Users).where(Users.id == user_id)
    await session.execute(query)
    await session.commit()

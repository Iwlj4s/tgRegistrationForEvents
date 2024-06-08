from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Users, Events, UsersEvents, ClosedEvents, Admins, Attendance, Inspectors


# USERS #
async def orm_user_add_info(session: AsyncSession, data: dict, message):
    obj = Users(
        tg_id=message.from_user.id,
        name=data['user_name'],
        phone=data['user_phone'],
        email=data['user_email'],
    )

    session.add(obj)

    await session.commit()


# Update User #
async def orm_update_user(session: AsyncSession, user_id: int, data, message):
    query = update(Users).where(Users.id == user_id).values(
        tg_id=message.from_user.id,
        name=data['user_name'],
        phone=data['user_phone'],
        email=data['user_email'], )

    await session.execute(query)
    await session.commit()


# Get user's tg_id #
async def orm_get_user_by_tg_id(session: AsyncSession, tg_id: int):
    query = select(Users).where(Users.tg_id == tg_id)
    result = await session.execute(query)
    user = result.scalar()
    return user


# EVENTS #
# Get events
async def orm_get_events(session: AsyncSession):
    query = select(Events)
    result = await session.execute(query)
    return result.scalars().all()


# Get users by event.id in usersEvents
async def orm_get_users_from_users_events(session: AsyncSession, event_id: int):
    query = select(UsersEvents).where(UsersEvents.user_event_id == int(event_id))
    result = await session.execute(query)
    return result.scalars().all()


# Get event id
async def orm_get_events_id(session: AsyncSession, event_id: int):
    query = select(Events).where(Events.id == event_id)
    result = await session.execute(query)
    event = result.scalar()
    return event


# Get User subscribed events
async def orm_get_user_subscribed_events(session: AsyncSession, user_id: int):
    query = select(UsersEvents).where(UsersEvents.user_tg_id == int(user_id))
    result = await session.execute(query)
    user_events = result.scalars().all()  # Fetch all results as a list
    return user_events


# Update Events
async def orm_update_event(session: AsyncSession, event_id: int, data):
    query = update(Events).where(Events.id == event_id).values(
        event_name=data["event_name"],
        event_address=data["event_address"],
        event_date=data["event_date"],
        event_time=data["event_time"])

    await session.execute(query)
    await session.commit()


# USERS EVENTS #
# Save selected Event in UsersEvents
async def orm_save_user_event_info(session: AsyncSession, tg_id, event_id: int):
    # get event name #
    events = select(Events.event_name).where(Events.id == event_id)
    result = await session.execute(events)
    event_name = result.scalar()

    # get event address
    event_data = await orm_get_events_id(session=session, event_id=int(event_id))
    event_address = event_data.event_address

    # get user info #
    user_tg_id = tg_id
    user_info = await orm_get_user_by_tg_id(session=session, tg_id=int(user_tg_id))

    # Add info in UsersEvents #
    user_event = UsersEvents(
        user_event_id=event_id,
        user_event_name=event_name,
        user_event_address=event_address,
        user_tg_id=user_info.tg_id,
        user_name=user_info.name,
        user_phone=user_info.phone,
        user_email=user_info.email
    )

    session.add(user_event)
    await session.commit()


# Update Users Events
async def orm_update_users_events(session: AsyncSession, user_tg_id: int, data: dict):
    print(f"Updating UsersEvents for user_tg_id: {user_tg_id}")
    print(f"Data to update: {data}")

    query = update(UsersEvents).where(UsersEvents.user_tg_id == user_tg_id).values(
        user_name=data['user_name'],
        user_phone=data['user_phone'],
        user_email=data['user_email']
    )
    result = await session.execute(query)
    await session.commit()

    print(f"UsersEvents updated successfully.")


# Update Users Events by event id
async def orm_update_users_events_by_event_id(session: AsyncSession, event_id: int, data: dict):
    print(f"Updating {event_id}")
    print(f"Data to update: {data}")

    query = update(UsersEvents).where(UsersEvents.user_event_id == event_id).values(
        user_event_name=data['event_name'],
        user_event_address=data['event_address'])

    result = await session.execute(query)
    await session.commit()

    print(f"UsersEvents updated successfully.")


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


# usersEvents by event_name
async def orm_get_event_by_event_name(session: AsyncSession, event_name: str):
    query = select(UsersEvents).filter(UsersEvents.user_event_name == event_name)
    result = await session.execute(query)
    event = result.scalar()
    return event


# Unsubscribe from event
async def orm_unsubscribe_from_event(session: AsyncSession, event_id: int, user_id: int):
    query = delete(UsersEvents).where(and_(UsersEvents.user_event_id == event_id, UsersEvents.user_tg_id == user_id))
    await session.execute(query)
    await session.commit()


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
        phone=data['user_phone'],
        email=data['user_email'],
    )

    await session.execute(query)
    await session.commit()


# Add info in ClosedEvents #
async def orm_add_info_in_closed_events(session: AsyncSession, event: Events):
    obj = ClosedEvents(
        event_id=event.id,
        event_address=event.event_address,
        event_name=event.event_name,
        event_date=event.event_date,
        event_time=event.event_time,
    )

    session.add(obj)
    await session.commit()


# Delete User
async def orm_delete_user(session: AsyncSession, user_id: int):
    query = delete(Users).where(Users.tg_id == user_id)
    await session.execute(query)
    await session.commit()


# Delete User From Events
async def orm_delete_user_from_events(session: AsyncSession, user_id: int):
    query = delete(UsersEvents).where(UsersEvents.user_tg_id == user_id)
    await session.execute(query)
    await session.commit()


# Add Event
async def orm_add_event(session: AsyncSession, data, message):
    max_id_query = select(func.max(Events.id))
    max_id_result = await session.execute(max_id_query)
    events_max_id = max_id_result.scalar()

    max_id_query_closed = select(func.max(ClosedEvents.event_id))
    max_id_result_closed = await session.execute(max_id_query_closed)
    closed_events_max_id = max_id_result_closed.scalar() or 0

    max_id = events_max_id

    if max_id is None:
        max_id = closed_events_max_id
    elif events_max_id < closed_events_max_id:
        max_id = closed_events_max_id

    else:
        max_id = events_max_id

    obj = Events(
        id=max_id + 1,
        event_name=data['event_name'],
        event_address=data["event_address"],
        event_date=data['event_date'],
        event_time=data['event_time'],
    )

    session.add(obj)

    await session.commit()


# Delete Event
async def orm_delete_event(session: AsyncSession, event_id: int):
    query = delete(Events).where(Events.id == event_id)
    await session.execute(query)
    await session.commit()


# Delete Event form UsersEvents
async def orm_delete_event_from_users_events(session: AsyncSession, event_id: int):
    query = delete(UsersEvents).where(UsersEvents.user_event_id == event_id)
    await session.execute(query)
    await session.commit()


# Get Event by Name
async def orm_get_event_by_name(session: AsyncSession, event_name: str):
    query = select(Events).filter(Events.event_name == str(event_name))
    result = await session.execute(query)
    events = result.scalar()
    return events


# Get Event by address
async def orm_get_event_by_address(session: AsyncSession, event_address: str):
    query = select(Events).filter(Events.event_address == str(event_address))
    result = await session.execute(query)
    events = result.scalar()
    return events


# Get Event by date
async def orm_get_event_by_date(session: AsyncSession, event_date: str):
    query = select(Events).filter(Events.event_date == str(event_date))
    result = await session.execute(query)
    events = result.scalar()
    return events


# Get Event by date
async def orm_get_event_by_time(session: AsyncSession, event_time: str):
    query = select(Events).filter(Events.event_time == str(event_time))
    result = await session.execute(query)
    events = result.scalar()
    return events


# INSPECTOR stuff #

# User already on event (user tg id)
async def orm_get_user_on_event_usr_tg_id(session: AsyncSession, tg_id: int):
    query = select(Attendance).filter(Attendance.user_tg_id == tg_id)
    result = await session.execute(query)
    events = result.scalar()
    return events


# User already on event (event_id)
async def orm_get_user_on_event_usr_event_id(session: AsyncSession, event_id: int):
    query = select(Attendance).filter(Attendance.user_event_id == event_id)
    result = await session.execute(query)
    events = result.scalar()
    return events


# Confirm user (add user info in attendance)
async def orm_confirm_user(session: AsyncSession, data):
    obj = Attendance(
        user_tg_id=data['user_tg_id'],
        user_event_id=data["user_event_id"],
        user_event_name=data["user_event_name"],
        inspector_id=data["inspector_id"],
        inspector_notes=data['inspector_notes'],
    )

    session.add(obj)

    await session.commit()


# ADD ADMIN #
async def orm_admin_add_info(session: AsyncSession, data: dict):
    obj = Admins(
        tg_id=data['admin_tg_id'],
        name=data['admin_name'],
        phone=data['admin_phone'],
        email=data['admin_email'],
    )

    session.add(obj)

    await session.commit()


# Get all admins
async def orm_get_admins(session: AsyncSession):
    query = select(Admins)
    result = await session.execute(query)
    return result.scalars().all()


# Delete Admin
async def orm_delete_admin(session: AsyncSession, admin_id: int):
    query = delete(Admins).where(Admins.tg_id == admin_id)
    await session.execute(query)
    await session.commit()


# Get one admin by id
async def orm_get_admin(session: AsyncSession, admin_id: int):
    query = select(Admins).where(Admins.id == admin_id)
    result = await session.execute(query)

    return result.scalar()


# Update Admins
async def orm_update_admin(session: AsyncSession, admin_id: int, data):
    query = update(Admins).where(Admins.id == admin_id).values(
        tg_id=data["tg_id"],
        name=data["admin_name"],
        phone=data["admin_phone"],
        email=data["admin_email"])

    await session.execute(query)
    await session.commit()


# Get Attendance
async def orm_get_attendance(session: AsyncSession):
    query = select(Attendance)
    result = await session.execute(query)
    return result.scalars().all()


# ADD INSPECTOR #
async def orm_inspector_add_info(session: AsyncSession, data: dict):
    obj = Inspectors(
        tg_id=data['tg_id'],
        name=data['inspector_name'],
        phone=data['inspector_phone'],
        email=data['inspector_email'],
    )

    session.add(obj)

    await session.commit()


# Get all inspectors
async def orm_get_inspectors(session: AsyncSession):
    query = select(Inspectors)
    result = await session.execute(query)
    return result.scalars().all()


# Delete Inspector
async def orm_delete_inspector(session: AsyncSession, inspector_id: int):
    query = delete(Inspectors).where(Inspectors.tg_id == inspector_id)
    await session.execute(query)
    await session.commit()


# Get one inspector by id
async def orm_get_inspector(session: AsyncSession, inspector_id: int):
    query = select(Inspectors).where(Inspectors.id == inspector_id)
    result = await session.execute(query)

    return result.scalar()


# Update Inspectors
async def orm_update_inspector(session: AsyncSession, inspector_id: int, data):
    query = update(Inspectors).where(Inspectors.id == inspector_id).values(
        tg_id=data["tg_id"],
        name=data["inspector_name"],
        phone=data["inspector_phone"],
        email=data["inspector_email"])

    await session.execute(query)
    await session.commit()
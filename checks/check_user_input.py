import datetime
import re

from sqlalchemy.ext.asyncio import AsyncSession

from email_validator import validate_email, EmailNotValidError

from database.orm_query import (orm_get_user_by_tg_id, orm_get_events_id, orm_get_users_events_by_tg_id,
                                orm_get_user_id_by_event_id)


# Check user input already not in db #
# using search by tg_id #
async def user_id_already_in_db(session: AsyncSession, tg_id: int):
    users = await orm_get_user_by_tg_id(session=session, tg_id=int(tg_id))
    for user in users:
        if user.tg_id == tg_id:
            return True
    return False


# Check user input correct event id #
async def user_input_id_event_is_correct(session: AsyncSession, event_id):
    events = await orm_get_events_id(session=session, event_id=int(event_id))
    if events:
        return True
    return False


# Check user input correct event id #
async def user_try_one_more(session, tg_id, event_id):
    user_events = await orm_get_users_events_by_tg_id(session=session, tg_id=int(tg_id))
    user_tg_id = await orm_get_user_id_by_event_id(session=session, event_id=int(event_id))
    if user_events and user_tg_id:
        return True

    return False


# Check user in UsersEvents
async def user_in_users_events(session, user_tg_id):
    user_tg_id = await orm_get_users_events_by_tg_id(session=session, tg_id=int(user_tg_id))
    if user_tg_id:
        return True

    else:
        return False


# Check user in UsersEvents for unsubscribe_from_event_
async def user_in_users_events_for_unsubscribe(session, user_tg_id, user_event_id):
    tg_id = await orm_get_users_events_by_tg_id(session=session, tg_id=int(user_tg_id))
    event_id = await orm_get_user_id_by_event_id(session=session, event_id=int(user_event_id))
    if tg_id and event_id:
        return True

    else:
        return False


# Check correct Phone input
async def validate_phone_input(phone_str):
    phone_pattern = r'\+7\(\d{3}\)\d{3}-\d{2}-\d{2}'
    if re.match(phone_pattern, phone_str):
        return True

    else:
        return False


# Check correct Email input
async def validate_email_input(email_str):
    try:
        email = validate_email(email_str)
        email = email.normalized

        return email
    except EmailNotValidError as e:
        return None


# Check correct Date input
async def validate_date_input(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
        return date
    except ValueError:
        return None


# Check correct Time input
async def validate_time_input(time_str):
    try:
        time = datetime.datetime.strptime(time_str, '%H:%M').time()
        return time
    except ValueError:
        return None

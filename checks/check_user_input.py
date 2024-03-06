from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_get_user_by_tg_id, orm_get_events_id


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

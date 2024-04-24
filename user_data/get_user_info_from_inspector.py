def get_user_info_from_inspector(data):
    user_name = data.get("user_name")
    user_tg_id = data.get("user_tg_id ")
    user_event_id = data.get("user_event_id")
    user_event_name = data.get("user_event_name")
    inspector_id = data.get("inspector_id")
    inspector_notes = data.get("inspector_notes")

    return (f"{user_name}\n"
            f"Телеграм id пользователя - {user_tg_id}\n"
            f"Id мероприятия пользователя - {user_event_id}\n"
            f"Имя мероприятия пользователя - {user_event_name}\n"
            f"Заметки - {inspector_notes}")

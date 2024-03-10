def get_user_info(data):
    user_name = data.get("user_name")
    user_phone = data.get("user_phone")
    user_email = data.get("user_email")

    return (f"Ваше имя - {user_name}\n"
            f"Ваш телефон - {user_phone}\n"
            f"Ваша почта - {user_email}\n")


def get_user_event(data):
    user_event_id = data.get("user_event_id")
    user_event_name = data.get("user_event_name")

    return (f"Id мероприятия - {user_event_id}\n"
            f"Мероприятие - {user_event_name}")
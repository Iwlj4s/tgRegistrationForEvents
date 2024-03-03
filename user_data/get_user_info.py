def get_user_info(data):
    event_id = data.get("event_id")
    user_name = data.get("user_name")
    user_phone = data.get("user_phone")
    user_email = data.get("user_email")

    return (f"Ваше имя - {user_name}\n"
            f"Ваш телефон - {user_phone}\n"
            f"Ваша почта - {user_email}\n"
            f"Id мероприятия - {event_id}")

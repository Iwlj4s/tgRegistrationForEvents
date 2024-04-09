def get_event_info(data):
    event_name = data.get("event_name")
    event_address = data.get("event_address")
    event_date = data.get("event_date")
    event_time = data.get("event_time")

    return (f"{event_name}\n"
            f"Адрес мероприятия - {event_address}\n"
            f"Дата мероприятия - {event_date}\n"
            f"Время мероприятия - {event_time}")

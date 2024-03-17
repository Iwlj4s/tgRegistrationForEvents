def get_event_info(data):
    event_name = data.get("event_name")
    event_date = data.get("event_date")
    event_time = data.get("event_time")

    return (f"{event_name}\n"
            f"Дата мероприятия - {event_date}\n"
            f"Время мероприятия - {event_time}")

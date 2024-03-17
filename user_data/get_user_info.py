def get_user_info(data):
    user_name = data.get("user_name")
    user_phone = data.get("user_phone")
    user_email = data.get("user_email")

    return (f"Ваше имя - {user_name}\n"
            f"Ваш телефон - {user_phone}\n"
            f"Ваша почта - {user_email}\n")


def get_user_data_for_admin(data):
    user_name = data.get("user_name")
    user_phone = data.get("user_phone")
    user_email = data.get("user_email")

    return (f"Ваше имя - {user_name}\n"
            f"Ваш телефон - {user_phone}\n"
            f"Ваша почта - {user_email}\n")
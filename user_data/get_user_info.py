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

    return (f"Имя пользователя - {user_name}\n"
            f"Телефон пользователя - {user_phone}\n"
            f"Эл.почта пользователя - {user_email}\n")


def get_admin_info(data):
    admin_tg_id = data.get("admin_tg_id")
    admin_name = data.get("admin_name")
    admin_phone = data.get("admin_phone")
    admin_email = data.get("admin_email")

    return (f"Телеграм id - {admin_tg_id}\n"
            f"Имя администратора - {admin_name}\n"
            f"Телефон администратора - {admin_phone}\n"
            f"Эл.почта администратора - {admin_email}\n")
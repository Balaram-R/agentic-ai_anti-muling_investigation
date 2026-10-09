from datetime import datetime


def format_timestamp(value):
    if not value:
        return ""

    try:
        if isinstance(value, datetime):
            dt = value
        else:
            text = str(value).replace("Z", "+00:00")
            dt = datetime.fromisoformat(text)

        return dt.astimezone().strftime("%d-%m-%Y %H:%M:%S")

    except (ValueError, TypeError):
        return str(value)
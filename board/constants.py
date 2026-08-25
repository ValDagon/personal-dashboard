"""Board constants. Russian labels for the public UI."""

WORLDS = ("freelance", "work", "hobby")

WORLD_LABEL = {
    "freelance": "Фриланс",
    "work": "Работа",
    "hobby": "Хобби",
}

STATUSES = ("now", "queued", "paused", "done", "delivered")

STATUS_LABEL = {
    "now": "сейчас",
    "queued": "очередь",
    "paused": "пауза",
    "done": "сделано",
    "delivered": "сдано клиенту",
}

OPEN_STATUSES = ("now", "queued", "paused")
ARCHIVE_STATUSES = ("done", "delivered")

OPEN_ORDER = ("now", "queued", "paused")

"""Board constants. Russian labels and HUD palette for the public UI."""

WORLDS = ("freelance", "work", "hobby")
WORLD_ORDER = WORLDS

HUD_SCENE = "#0B1220"
HUD_PANEL = "#121A2C"
HUD_INK = "#E8F1FF"
HUD_MUTED = "#8AA0B8"
HUD_RULE = "#1A3D52"
HUD_CHROME = "#3EC4FF"

WORLD_COLORS = {
    "freelance": "#FFB14A",
    "work": "#FF6BB5",
    "hobby": "#3EC4FF",
}

# Open-status fills for Plotly + CSS legend. Same family as worlds, not gray/white.
STATUS_COLORS = {
    "now": WORLD_COLORS["hobby"],
    "queued": WORLD_COLORS["freelance"],
    "paused": WORLD_COLORS["work"],
}

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

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

# Open-status fills. Same family as worlds, independent map (never near-white or gray).
STATUS_COLORS = {
    "now": "#3EC4FF",
    "queued": "#FFB14A",
    "paused": "#FF6BB5",
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


def css_custom_properties() -> str:
    """Single source of truth for HUD tokens injected after assets/style.css."""
    return (
        ":root {\n"
        f"  --paper: {HUD_SCENE};\n"
        f"  --panel: {HUD_PANEL};\n"
        f"  --ink: {HUD_INK};\n"
        f"  --muted: {HUD_MUTED};\n"
        f"  --rule: {HUD_RULE};\n"
        f"  --freelance: {WORLD_COLORS['freelance']};\n"
        f"  --work: {WORLD_COLORS['work']};\n"
        f"  --hobby: {WORLD_COLORS['hobby']};\n"
        f"  --chrome: {HUD_CHROME};\n"
        f"  --status-now: {STATUS_COLORS['now']};\n"
        f"  --status-queued: {STATUS_COLORS['queued']};\n"
        f"  --status-paused: {STATUS_COLORS['paused']};\n"
        "}\n"
    )

"""Character Initialization Feature"""

def init_character_data():
    """Initialize default character data structure"""
    return {
        "level": 1,
        "total_points": 0,
        "current_week_points": 0,
        "stats": {
            "strength": {"level": 1, "xp": 0, "xp_to_next": 100},
            "intellect": {"level": 1, "xp": 0, "xp_to_next": 100},
            "discipline": {"level": 1, "xp": 0, "xp_to_next": 100},
            "energy": {"level": 1, "xp": 0, "xp_to_next": 100},
            "influence": {"level": 1, "xp": 0, "xp_to_next": 100}
        }
    }

def init_streaks():
    """Initialize streak data structure"""
    return {
        "no_porn": {"current": 0, "longest": 0, "multiplier": 1.0, "base_points": 10, "daily_bonus": 2, "last_date": ""},
        "workout": {"current": 0, "longest": 0, "multiplier": 1.0, "base_points": 25, "last_date": ""},
        "sleep_7h": {"current": 0, "longest": 0, "multiplier": 1.0, "base_points": 8, "last_date": ""},
        "morning_routine": {"current": 0, "longest": 0, "multiplier": 1.0, "base_points": 5, "last_date": ""},
        "no_doomscroll": {"current": 0, "longest": 0, "multiplier": 1.0, "base_points": 8, "last_date": ""},
        "deep_work": {"current": 0, "longest": 0, "multiplier": 1.0, "base_points": 20, "last_date": ""},
        "reading": {"current": 0, "longest": 0, "multiplier": 1.0, "base_points": 10, "last_date": ""},
        "screen_time_under_2h": {"current": 0, "longest": 0, "multiplier": 1.0, "base_points": 15, "last_date": ""},
        "meditation": {"current": 0, "longest": 0, "multiplier": 1.0, "base_points": 8, "last_date": ""},
        "coding_practice": {"current": 0, "longest": 0, "multiplier": 1.0, "base_points": 15, "last_date": ""}
    }

"""Character Initialization Feature"""
 
 
class CharacterInitializer:
    """Builds default data structures for new characters."""
 
    STATS = ('body', 'mind', 'soul')
 
    STREAKS = {
        'no_porn':             {'base_points': 10, 'daily_bonus': 2},
        'workout':             {'base_points': 25},
        'sleep_7h':            {'base_points': 8},
        'morning_routine':     {'base_points': 5},
        'no_doomscroll':       {'base_points': 8},
        'deep_work':           {'base_points': 20},
        'reading':             {'base_points': 10},
        'screen_time_under_2h':{'base_points': 15},
        'meditation':          {'base_points': 8},
        'coding_practice':     {'base_points': 15},
    }
 
    @classmethod
    def default_stat(cls) -> dict:
        return {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0}
 
    @classmethod
    def init_character_data(cls) -> dict:
        return {
            'level': 1,
            'total_points': 0,
            'current_week_points': 0,
            'stats': {stat: cls.default_stat() for stat in cls.STATS},
        }
 
    @classmethod
    def init_streaks(cls) -> dict:
        base = {'current': 0, 'longest': 0, 'multiplier': 1.0, 'last_date': ''}
        result = {}
        for name, extras in cls.STREAKS.items():
            entry = {**base, **extras}
            result[name] = entry
        return result
 
 
# ── Module-level convenience wrappers (keeps existing call sites working) ──────
 
def init_character_data() -> dict:
    return CharacterInitializer.init_character_data()
 
def init_streaks() -> dict:
    return CharacterInitializer.init_streaks()

"""Streak Management"""
from datetime import datetime
 
 
class StreakManager:
    """Handles streak tracking and XP distribution."""
 
    # Maps streak name → which stat receives the XP, and how (full or split)
    STREAK_STAT_MAP = {
        # body: physical training + recovery
        'workout':              ('body', 1.0),
        'sleep_7h':             ('body', 1.0),
        'meditation':           ('body', 1.0),
 
        # mind: focus, discipline, learning
        'deep_work':            ('mind', 1.0),
        'reading':              ('mind', 1.0),
        'coding_practice':      ('mind', 1.0),
        'no_porn':              ('mind', 1.0),
        'morning_routine':      ('mind', 1.0),
        'no_doomscroll':        ('mind', 1.0),
        'screen_time_under_2h': ('mind', 1.0),
    }
 
    @staticmethod
    def multiplier(streak_days: int) -> float:
        if streak_days >= 30: return 2.0
        if streak_days >= 7:  return 1.5
        return 1.0
 
    @classmethod
    def _calc_points(cls, streak_name: str, streak: dict) -> int:
        mult = cls.multiplier(streak['current'])
        base = streak['base_points']
        if streak_name == 'no_porn':
            bonus = streak.get('daily_bonus', 2) * (streak['current'] - 1)
            return int((base + bonus) * mult)
        return int(base * mult)
 
    @classmethod
    def _advance(cls, streak: dict, log_date: str, log_dt: datetime) -> None:
        """Increment or reset a single streak in-place."""
        last = streak.get('last_date', '')
        if last:
            try:
                days = (log_dt - datetime.strptime(last, '%Y-%m-%d')).days
                if days == 1:
                    streak['current'] += 1
                elif days > 1:
                    streak['current'] = 1
                # days == 0 → same day, no change
            except ValueError:
                streak['current'] = 1
        else:
            streak['current'] = 1
 
        streak['last_date'] = log_date
        if streak['current'] > streak.get('longest', 0):
            streak['longest'] = streak['current']
        streak['multiplier'] = cls.multiplier(streak['current'])
 
    @classmethod
    def _break_stale(cls, streaks: dict, completed: set, log_dt: datetime) -> None:
        """Reset any streak that wasn't completed and has gone stale."""
        for name, streak in streaks.items():
            if name in completed or not streak.get('last_date'):
                continue
            try:
                days = (log_dt - datetime.strptime(streak['last_date'], '%Y-%m-%d')).days
                if days >= 1:
                    streak['current'] = 0
                    streak['multiplier'] = 1.0
            except ValueError:
                continue
 
    @classmethod
    def update(cls, streaks: dict, completed: list, log_date: str) -> tuple:
        """
        Update all streaks and return (streaks, total_points, stat_xp).
        Replaces the old update_streaks() function.
        """
        log_dt = datetime.strptime(log_date, '%Y-%m-%d')
        completed_set = set(completed)
 
        cls._break_stale(streaks, completed_set, log_dt)
 
        total_points = 0
        stat_xp = {'body': 0, 'mind': 0, 'soul': 0}
 
        for name in completed:
            if name not in streaks:
                continue
            streak = streaks[name]
            cls._advance(streak, log_date, log_dt)
            points = cls._calc_points(name, streak)
            total_points += points
 
            stat, fraction = cls.STREAK_STAT_MAP.get(name, ('mind', 1.0))
            stat_xp[stat] += int(points * fraction)
 
        return streaks, total_points, stat_xp
 
 
# ── Module-level convenience wrapper (keeps existing call sites working) ───────
 
def update_streaks(streaks: dict, streaks_completed: list, log_date: str) -> tuple:
    return StreakManager.update(streaks, streaks_completed, log_date)

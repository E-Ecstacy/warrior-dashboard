"""Streak Management"""
from datetime import datetime, timedelta

def calculate_streak_multiplier(streak_days):
    """Calculate multiplier based on streak length"""
    if streak_days >= 30:
        return 2.0
    elif streak_days >= 7:
        return 1.5
    return 1.0

def update_streaks(streaks, streaks_completed, log_date):
    """Update all streaks based on completed activities"""
    log_datetime = datetime.strptime(log_date, '%Y-%m-%d')
    
    # Reset broken streaks
    for streak_name, streak in streaks.items():
        if streak.get('last_date'):
            try:
                last_datetime = datetime.strptime(streak['last_date'], '%Y-%m-%d')
                days_between = (log_datetime - last_datetime).days
                
                if days_between > 1 and streak_name not in streaks_completed:
                    streak['current'] = 0
                    streak['multiplier'] = 1.0
                elif days_between == 1 and streak_name not in streaks_completed:
                    streak['current'] = 0
                    streak['multiplier'] = 1.0
            except:
                continue
    
    # Update completed streaks
    total_streak_points = 0
    stat_xp = {'strength': 0, 'intellect': 0, 'discipline': 0, 'energy': 0, 'influence': 0}
    
    for streak_name in streaks_completed:
        if streak_name not in streaks:
            continue
            
        streak = streaks[streak_name]
        
        if streak.get('last_date'):
            try:
                last_datetime = datetime.strptime(streak['last_date'], '%Y-%m-%d')
                days_between = (log_datetime - last_datetime).days
                
                if days_between == 1:
                    streak['current'] += 1
                elif days_between == 0:
                    pass  # Same day
                else:
                    streak['current'] = 1
            except:
                streak['current'] = 1
        else:
            streak['current'] = 1
        
        streak['last_date'] = log_date
        if streak['current'] > streak['longest']:
            streak['longest'] = streak['current']
        
        # Calculate points
        multiplier = calculate_streak_multiplier(streak['current'])
        streak['multiplier'] = multiplier
        base = streak['base_points']
        
        if streak_name == 'no_porn':
            bonus = streak.get('daily_bonus', 2) * (streak['current'] - 1)
            points = int((base + bonus) * multiplier)
        else:
            points = int(base * multiplier)
        
        total_streak_points += points
        
        # Add stat XP
        if streak_name in ['workout', 'sleep_7h']:
            stat_xp['strength'] += int(points * 0.5)
            stat_xp['energy'] += int(points * 0.5)
        elif streak_name in ['deep_work', 'reading', 'coding_practice']:
            stat_xp['intellect'] += points
        elif streak_name in ['no_porn', 'morning_routine', 'no_doomscroll', 'screen_time_under_2h']:
            stat_xp['discipline'] += points
        elif streak_name == 'meditation':
            stat_xp['energy'] += points
    
    return streaks, total_streak_points, stat_xp

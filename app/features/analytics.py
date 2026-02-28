"""Analytics Calculations"""
from datetime import datetime, timedelta
from collections import defaultdict

def calculate_analytics(daily_logs):
    """Calculate analytics from daily logs"""
    if not daily_logs:
        return {}
    
    # Basic stats
    total_days = len(daily_logs)
    total_points = sum(log['total_points'] for log in daily_logs)
    avg_points = int(total_points / total_days) if total_days > 0 else 0
    
    # Best/worst days
    best_day = max(daily_logs, key=lambda x: x['total_points']) if daily_logs else None
    worst_day = min(daily_logs, key=lambda x: x['total_points']) if daily_logs else None
    
    # Activity breakdown
    activity_counts = defaultdict(int)
    for log in daily_logs:
        tier2 = log.get('tier2', {})
        for activity, done in tier2.items():
            if done:
                activity_counts[activity] += 1
    
    top_activities = sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Weekly trend
    last_7_days = daily_logs[-7:] if len(daily_logs) >= 7 else daily_logs
    weekly_points = [log['total_points'] for log in last_7_days]
    
    return {
        'total_days': total_days,
        'total_points': total_points,
        'average_points': avg_points,
        'best_day': {
            'date': best_day['date'] if best_day else None,
            'points': best_day['total_points'] if best_day else 0
        },
        'worst_day': {
            'date': worst_day['date'] if worst_day else None,
            'points': worst_day['total_points'] if worst_day else 0
        },
        'top_activities': [{'name': name, 'count': count} for name, count in top_activities],
        'weekly_trend': weekly_points
    }

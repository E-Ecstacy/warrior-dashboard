"""Character Level Management"""

def calculate_level_up(total_points):
    """Calculate character level from total points"""
    level = 1
    points_for_next = 100
    remaining = total_points
    
    while remaining >= points_for_next:
        remaining -= points_for_next
        level += 1
        points_for_next = int(100 * (1.2 ** (level - 1)))
    
    return level

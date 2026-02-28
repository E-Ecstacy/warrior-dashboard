"""Activity Points Calculation"""

ACTIVITY_POINTS = {
    # Tier 2 - Physical
    'full_workout': 25, 'light_exercise': 12, 'push_ups_100': 20,
    'steps_10k': 8, 'stretching': 5, 'cold_shower': 3,
    
    # Mental
    'deep_work': 20, 'study_pomodoro': 15, 'project_dev': 18,
    'part_time_job': 20, 'new_skill': 12,
    
    # Learning
    'read_book': 10, 'kinnu': 8, 'online_course': 15,
    'code_practice': 15, 'journal': 5,
    
    # Digital Wellness
    'screen_under_2h': 15, 'screen_2_4h': 8,
    'no_phone_morning': 5, 'no_phone_night': 5,
    
    # Life Admin
    'plan_tomorrow': 3, 'organize_space': 5, 'budget_review': 8,
    
    # Mindfulness
    'meditation': 8, 'gratitude': 3, 'breathwork': 5, 'nature_walk': 7,
    
    # Creative
    'code_project': 25, 'write_docs': 10, 'build_design': 20, 'open_source': 15,
    
    # Social
    'meaningful_conversation': 8, 'help_code': 10, 'call_family': 5,
    'group_activity': 7, 'mentor_session': 8, 'networking': 6,
    'compliment_someone': 2, 'thank_someone': 2, 'check_in': 3, 'quality_time': 10,
    
    # Tier 3
    'flow_state_4h': 80, 'zero_screens': 100, 'complete_todo': 50,
    'cold_exposure': 30, 'new_algorithm': 60, 'teach_code': 40
}

def calculate_activity_points(activities):
    """Calculate total points from activities dict"""
    total = 0
    for activity, completed in activities.items():
        if completed and activity in ACTIVITY_POINTS:
            total += ACTIVITY_POINTS[activity]
    return total

def calculate_tier1_points(tier1_complete):
    """Calculate Tier 1 foundation bonus"""
    return 20 if tier1_complete else 0

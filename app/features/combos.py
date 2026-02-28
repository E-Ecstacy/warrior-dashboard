"""Combo Detection System"""

COMBOS = {
    "ultimate_day": {
        "name": "Ultimate Day",
        "activities": ["full_workout", "deep_work", "meditation", "read_book", "code_practice", "meaningful_conversation"],
        "bonus_points": 50
    },
    "balanced_beast": {
        "name": "Balanced Beast",
        "activities": ["full_workout", "deep_work", "meditation", "read_book"],
        "bonus_points": 25
    },
    "creative_fitness": {
        "name": "Creative Fitness",
        "activities": ["full_workout", "code_project", "build_design"],
        "bonus_points": 22
    },
    "productive_start": {
        "name": "Productive Start",
        "activities": ["full_workout", "deep_work", "plan_tomorrow"],
        "bonus_points": 20
    },
    "code_athlete": {
        "name": "Code Athlete",
        "activities": ["full_workout", "code_practice", "stretching"],
        "bonus_points": 18
    },
    "social_fitness": {
        "name": "Social Fitness",
        "activities": ["full_workout", "meaningful_conversation", "group_activity"],
        "bonus_points": 18
    },
    "morning_warrior": {
        "name": "Morning Warrior",
        "activities": ["full_workout", "cold_shower", "meditation"],
        "bonus_points": 15
    },
    "mind_body_stack": {
        "name": "Mind-Body Stack",
        "activities": ["meditation", "full_workout", "journal"],
        "bonus_points": 15
    },
    "cardio_coder": {
        "name": "Cardio Coder",
        "activities": ["steps_10k", "code_practice", "online_course"],
        "bonus_points": 15
    },
    "strength_scholar": {
        "name": "Strength Scholar",
        "activities": ["push_ups_100", "study_pomodoro", "new_skill"],
        "bonus_points": 15
    },
    "active_learner": {
        "name": "Active Learner",
        "activities": ["light_exercise", "online_course", "nature_walk"],
        "bonus_points": 14
    },
    "jack_of_exercises": {
        "name": "Jack of Exercises",
        "activities": ["light_exercise", "project_dev", "read_book"],
        "bonus_points": 12
    },
    "recovery_master": {
        "name": "Recovery Master",
        "activities": ["stretching", "cold_shower", "meditation", "breathwork"],
        "bonus_points": 12
    },
    "zen_productivity": {
        "name": "Zen Productivity",
        "activities": ["meditation", "deep_work", "organize_space"],
        "bonus_points": 12
    },
    "wellness_warrior": {
        "name": "Wellness Warrior",
        "activities": ["meditation", "stretching", "gratitude"],
        "bonus_points": 10
    }
}

def check_combos(activities_done):
    """Check which combos are activated"""
    detected = []
    
    for combo_id, combo_data in COMBOS.items():
        if all(activity in activities_done for activity in combo_data["activities"]):
            detected.append({
                "id": combo_id,
                "name": combo_data["name"],
                "bonus_points": combo_data["bonus_points"]
            })
    
    return detected

def calculate_combo_bonus(combos):
    """Calculate total bonus points from combos"""
    return sum(combo['bonus_points'] for combo in combos)

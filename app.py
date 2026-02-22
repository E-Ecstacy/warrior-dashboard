"""
Warrior Dashboard - Gamified Productivity Tracker
A full-stack web application for tracking daily activities, streaks, and character progression
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from db_adapter import DatabaseAdapter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'warrior-dashboard-secret-key-2024'

# Initialize database adapter (uses SQLite by default)
db = DatabaseAdapter(storage_type='sqlite')

# Legacy - for backward compatibility
DATA_FILE = 'data/character_data.json'

# Initialize data structure
def init_data():
    """Initialize default character data"""
    return {
        "character": {
            "name": "Warrior",
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
        },
        "streaks": {
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
        },
        "streak_insurance": {
            "tokens": 0,
            "max_tokens": 3,
            "tokens_earned_total": 0
        },
        "daily_log": [],
        "weekly_targets": {
            "current_week": 1,
            "target_points": 600,
            "weeks_completed": 0,
            "weeks_won": 0
        },
        "skill_tree": {
            "available_points": 0,
            "unlocked": [],
            "locked": [
                {"id": "advanced_workout", "name": "Advanced Workout Program", "cost": 500, "category": "strength"},
                {"id": "premium_learning", "name": "Premium Learning Platform", "cost": 500, "category": "intellect"},
                {"id": "coding_course", "name": "Advanced Programming Course", "cost": 500, "category": "intellect"},
                {"id": "project_equipment", "name": "New Dev Equipment/Tools", "cost": 500, "category": "influence"},
                {"id": "cheat_day", "name": "Guilt-Free Rest Day", "cost": 500, "category": "energy"},
                {"id": "weekend_trip", "name": "Weekend Experience/Trip", "cost": 1000, "category": "energy"},
                {"id": "mentor_session", "name": "Mentor/Coach Session", "cost": 1000, "category": "influence"},
                {"id": "dream_purchase", "name": "Major Dream Purchase", "cost": 2500, "category": "influence"},
                {"id": "certification", "name": "Professional Certification", "cost": 2500, "category": "intellect"}
            ]
        },
        "achievements": {
            "earned": [],
            "available": [
                {"id": "week_warrior", "name": "Week Warrior", "description": "7 days of 100+ points", "points_bonus": 50},
                {"id": "balanced_life", "name": "Balanced Life", "description": "Hit all 5 stat categories in one week", "points_bonus": 50},
                {"id": "comeback_kid", "name": "Comeback Kid", "description": "200+ points after a <50p day", "points_bonus": 30},
                {"id": "flow_state", "name": "Flow State Master", "description": "4+ hours deep work in one day", "points_bonus": 80},
                {"id": "digital_monk", "name": "Digital Monk", "description": "Zero screens entire day", "points_bonus": 100},
                {"id": "streak_legend", "name": "Streak Legend", "description": "30-day streak on any activity", "points_bonus": 100}
            ]
        },
        "personal_records": {
            "exercises": {}
        },
        "notes": {
            "daily_notes": [],
            "plans": []
        },
        "daily_challenge": {
            "current_challenge": None,
            "date": "",
            "completed": False,
            "history": []
        },
        "combo_system": {
            "active_combo": [],
            "combo_multiplier": 1.0,
            "best_combo": 0,
            "total_combos": 0
        },
        "nemesis_mode": {
            "active": False,
            "non_negotiables": [],
            "nemesis_gauge": 0,
            "breaks_this_month": 0,
            "forced_rest_date": None
        },
        "ghost_data": {
            "weekly_averages": [],
            "best_week": 0,
            "best_day": 0,
            "total_days_logged": 0
        },
        "analytics": {
            "activity_breakdown": {},
            "best_day_of_week": None,
            "productivity_hours": {},
            "monthly_totals": []
        },
        "budget_tracker": {
            "current_balance": 0,
            "transactions": [],
            "categories": {
                "income": ["Salary", "Freelance", "Gifts", "Other Income"],
                "expenses": ["Food", "Transport", "Entertainment", "Fitness", "Learning", "Bills", "Shopping", "Other"]
            },
            "monthly_budget": {
                "Food": 0,
                "Transport": 0,
                "Entertainment": 0,
                "Fitness": 0,
                "Learning": 0,
                "Bills": 0,
                "Shopping": 0,
                "Other": 0
            },
            "monthly_summary": []
        },
        "workout_sessions": {
            "templates": {},
            "history": []
        }
    }

def load_data():
    """Load data from current storage (JSON or SQLite)"""
    data = db.load_data()
    if data is None:
        data = init_data()
        save_data(data)
    return data

def save_data(data):
    """Save data to current storage (JSON or SQLite)"""
    db.save_data(data)

def calculate_streak_multiplier(days):
    """Calculate streak multiplier based on days"""
    if days >= 30:
        return 2.0
    elif days >= 7:
        return 1.5
    return 1.0

def calculate_stat_xp_needed(level):
    """Calculate XP needed for next level"""
    return level * 100

def add_xp_to_stat(data, stat_name, xp):
    """Add XP to a stat and handle level ups"""
    stat = data['character']['stats'][stat_name]
    stat['xp'] += xp
    
    # Check for level up
    while stat['xp'] >= stat['xp_to_next']:
        stat['xp'] -= stat['xp_to_next']
        stat['level'] += 1
        stat['xp_to_next'] = calculate_stat_xp_needed(stat['level'])

def generate_daily_challenge():
    """Generate a random daily challenge"""
    import random
    
    challenges = [
        {"id": "no_caffeine", "name": "No Caffeine Today", "description": "No coffee, tea, or energy drinks", "points": 15, "category": "discipline"},
        {"id": "read_1h", "name": "Read for 1 Hour Straight", "description": "No breaks, full focus reading", "points": 20, "category": "intellect"},
        {"id": "ice_bath", "name": "10-Minute Ice Bath", "description": "Cold exposure challenge", "points": 30, "category": "strength"},
        {"id": "teach_someone", "name": "Teach Someone Something", "description": "Share knowledge with another person", "points": 25, "category": "influence"},
        {"id": "silent_workout", "name": "No Music During Workout", "description": "Pure focus, no audio", "points": 10, "category": "discipline"},
        {"id": "no_social_media", "name": "Zero Social Media", "description": "Not even a peek", "points": 20, "category": "discipline"},
        {"id": "wake_5am", "name": "Wake Up at 5 AM", "description": "Early bird special", "points": 15, "category": "discipline"},
        {"id": "100_burpees", "name": "100 Burpees", "description": "All at once or throughout day", "points": 25, "category": "strength"},
        {"id": "no_screens_evening", "name": "No Screens After 8 PM", "description": "Evening digital detox", "points": 15, "category": "energy"},
        {"id": "help_stranger", "name": "Help a Stranger", "description": "Random act of kindness", "points": 20, "category": "influence"},
        {"id": "30min_meditation", "name": "30-Minute Meditation", "description": "Extended mindfulness session", "points": 25, "category": "energy"},
        {"id": "no_sugar", "name": "No Sugar Today", "description": "Zero added sugars", "points": 15, "category": "discipline"},
        {"id": "learn_new_concept", "name": "Learn Something Completely New", "description": "Outside your comfort zone", "points": 20, "category": "intellect"},
        {"id": "write_1000_words", "name": "Write 1000 Words", "description": "Journal, blog, or creative writing", "points": 20, "category": "intellect"},
        {"id": "no_complaints", "name": "Don't Complain All Day", "description": "Catch yourself, stay positive", "points": 15, "category": "discipline"}
    ]
    
    return random.choice(challenges)

def check_combo(activities_done):
    """Check if activities form a combo chain - returns list of detected combos with bonus points"""
    combos = {
        "morning_warrior": {
            "activities": ["full_workout", "cold_shower", "meditation"],
            "bonus_points": 15,
            "name": "Morning Warrior",
            "description": "Workout + Cold Shower + Meditation"
        },
        "productive_start": {
            "activities": ["full_workout", "deep_work", "plan_tomorrow"],
            "bonus_points": 20,
            "name": "Productive Start",
            "description": "Workout + Deep Work + Planning"
        },
        "code_athlete": {
            "activities": ["full_workout", "code_practice", "stretching"],
            "bonus_points": 18,
            "name": "Code Athlete",
            "description": "Workout + Code + Stretching"
        },
        "jack_of_exercises": {
            "activities": ["light_exercise", "project_dev", "read_book"],
            "bonus_points": 12,
            "name": "Jack of Exercises",
            "description": "Light Exercise + Project + Reading"
        },
        "mind_body_stack": {
            "activities": ["meditation", "full_workout", "journal"],
            "bonus_points": 15,
            "name": "Mind-Body Stack",
            "description": "Meditation + Workout + Journaling"
        },
        "wellness_warrior": {
            "activities": ["meditation", "stretching", "gratitude"],
            "bonus_points": 10,
            "name": "Wellness Warrior",
            "description": "Meditation + Stretching + Gratitude"
        },
        "social_fitness": {
            "activities": ["full_workout", "meaningful_conversation", "group_activity"],
            "bonus_points": 18,
            "name": "Social Fitness",
            "description": "Workout + Conversation + Group Activity"
        },
        "recovery_master": {
            "activities": ["stretching", "cold_shower", "meditation", "breathwork"],
            "bonus_points": 12,
            "name": "Recovery Master",
            "description": "Stretching + Cold Shower + Meditation + Breathwork"
        },
        "balanced_beast": {
            "activities": ["full_workout", "deep_work", "meditation", "read_book"],
            "bonus_points": 25,
            "name": "Balanced Beast",
            "description": "Workout + Deep Work + Meditation + Reading"
        },
        "cardio_coder": {
            "activities": ["steps_10k", "code_practice", "online_course"],
            "bonus_points": 15,
            "name": "Cardio Coder",
            "description": "10k Steps + Code Practice + Online Course"
        },
        "strength_scholar": {
            "activities": ["push_ups_100", "study_pomodoro", "new_skill"],
            "bonus_points": 15,
            "name": "Strength Scholar",
            "description": "100 Push-ups + Study + New Skill"
        },
        "zen_productivity": {
            "activities": ["meditation", "deep_work", "organize_space"],
            "bonus_points": 12,
            "name": "Zen Productivity",
            "description": "Meditation + Deep Work + Organize Space"
        },
        "active_learner": {
            "activities": ["light_exercise", "online_course", "nature_walk"],
            "bonus_points": 14,
            "name": "Active Learner",
            "description": "Light Exercise + Course + Nature Walk"
        },
        "creative_fitness": {
            "activities": ["full_workout", "code_project", "build_design"],
            "bonus_points": 22,
            "name": "Creative Fitness",
            "description": "Workout + Code Project + Design"
        },
        "ultimate_day": {
            "activities": ["full_workout", "deep_work", "meditation", "read_book", "code_practice", "meaningful_conversation"],
            "bonus_points": 50,
            "name": "Ultimate Day",
            "description": "Workout + Deep Work + Meditation + Reading + Code + Conversation"
        }
    }
    
    detected_combos = []
    for combo_id, combo_data in combos.items():
        if all(activity in activities_done for activity in combo_data["activities"]):
            detected_combos.append(combo_data)
    
    return detected_combos

def check_nemesis_break(data, daily_entry):
    """Check if user broke any non-negotiable rules"""
    if not data.get('nemesis_mode', {}).get('active', False):
        return False
    
    non_negotiables = data['nemesis_mode'].get('non_negotiables', [])
    streaks_completed = daily_entry.get('streaks_completed', [])
    
    # Check if any non-negotiable was broken
    for non_neg in non_negotiables:
        if non_neg not in streaks_completed:
            return True
    
    return False

def add_xp_to_stat(data, stat_name, xp):
    """Add XP to a stat and handle level ups"""
    stat = data['character']['stats'][stat_name]
    stat['xp'] += xp
    
    # Check for level up
    while stat['xp'] >= stat['xp_to_next']:
        stat['xp'] -= stat['xp_to_next']
        stat['level'] += 1
        stat['xp_to_next'] = calculate_stat_xp_needed(stat['level'])

def check_achievements(data, daily_entry):
    """Check and unlock achievements based on activity"""
    earned = []
    
    # Week Warrior - 7 days of 100+ points
    if len(data['daily_log']) >= 7:
        recent_week = data['daily_log'][-7:]
        if all(day.get('total_points', 0) >= 100 for day in recent_week):
            achievement = next((a for a in data['achievements']['available'] if a['id'] == 'week_warrior'), None)
            if achievement and achievement['id'] not in [a['id'] for a in data['achievements']['earned']]:
                earned.append(achievement)
    
    # Flow State Master - 4+ hours deep work
    if daily_entry.get('tier3_flow_state', False):
        achievement = next((a for a in data['achievements']['available'] if a['id'] == 'flow_state'), None)
        if achievement and achievement['id'] not in [a['id'] for a in data['achievements']['earned']]:
            earned.append(achievement)
    
    # Digital Monk - Zero screens
    if daily_entry.get('tier3_digital_monk', False):
        achievement = next((a for a in data['achievements']['available'] if a['id'] == 'digital_monk'), None)
        if achievement and achievement['id'] not in [a['id'] for a in data['achievements']['earned']]:
            earned.append(achievement)
    
    # Streak Legend - 30-day streak
    for streak_name, streak_data in data['streaks'].items():
        if streak_data['current'] >= 30:
            achievement = next((a for a in data['achievements']['available'] if a['id'] == 'streak_legend'), None)
            if achievement and achievement['id'] not in [a['id'] for a in data['achievements']['earned']]:
                earned.append(achievement)
                break
    
    return earned

@app.route('/')
def index():
    """Main dashboard page"""
    data = load_data()
    return render_template('index.html', data=data)

@app.route('/api/storage-info')
def storage_info():
    """Get current storage type and info"""
    storage_type = db.get_storage_type()
    
    info = {
        'storage_type': storage_type,
        'can_migrate': storage_type == 'json',
        'database_file': 'data/warrior_dashboard.db' if storage_type == 'sqlite' else None,
        'json_file': 'data/character_data.json' if storage_type == 'json' else None
    }
    
    return jsonify(info)

@app.route('/api/character')
def get_character():
    """Get character data"""
    data = load_data()
    return jsonify(data['character'])

@app.route('/api/streaks')
def get_streaks():
    """Get all streaks"""
    data = load_data()
    
    # Calculate multipliers
    for streak_name, streak_data in data['streaks'].items():
        streak_data['multiplier'] = calculate_streak_multiplier(streak_data['current'])
    
    return jsonify(data['streaks'])

@app.route('/api/daily-log', methods=['GET', 'POST'])
def daily_log():
    """Get or create daily log entry"""
    data = load_data()
    
    if request.method == 'POST':
        entry = request.json
        today = datetime.now().strftime('%Y-%m-%d')
        entry['date'] = today
        
        # Calculate total points
        total_points = 0
        stat_xp = defaultdict(int)
        
        # Tier 1 activities (foundation)
        tier1_complete = entry.get('tier1_complete', False)
        
        # Tier 2 activities
        tier2 = entry.get('tier2', {})
        
        # Physical Health (STRENGTH)
        if tier2.get('full_workout'): 
            total_points += 25
            stat_xp['strength'] += 25
        if tier2.get('light_exercise'): 
            total_points += 12
            stat_xp['strength'] += 12
        if tier2.get('push_ups_100'): 
            total_points += 20
            stat_xp['strength'] += 20
        if tier2.get('steps_10k'): 
            total_points += 8
            stat_xp['strength'] += 8
        if tier2.get('stretching'): 
            total_points += 5
            stat_xp['strength'] += 5
        if tier2.get('cold_shower'): 
            total_points += 3
            stat_xp['strength'] += 3
        
        # Mental Development (INTELLECT)
        if tier2.get('deep_work'):
            quality = tier2.get('deep_work_quality', 'B')
            base_points = 20
            if quality == 'A':
                points = base_points
            elif quality == 'B':
                points = int(base_points * 0.75)
            else:  # C
                points = int(base_points * 0.5)
            total_points += points
            stat_xp['intellect'] += points
        
        if tier2.get('study_pomodoro'): 
            total_points += 8
            stat_xp['intellect'] += 8
        if tier2.get('project_dev'): 
            total_points += 15
            stat_xp['intellect'] += 15
        if tier2.get('part_time_job'): 
            total_points += 20
            stat_xp['intellect'] += 20
        if tier2.get('new_skill'): 
            total_points += 10
            stat_xp['intellect'] += 10
        if tier2.get('read_book'): 
            total_points += 10
            stat_xp['intellect'] += 10
        if tier2.get('kinnu'): 
            total_points += 5
            stat_xp['intellect'] += 5
        if tier2.get('online_course'): 
            total_points += 12
            stat_xp['intellect'] += 12
        if tier2.get('code_practice'): 
            total_points += 15
            stat_xp['intellect'] += 15
        if tier2.get('journal'): 
            total_points += 5
            stat_xp['intellect'] += 5
        
        # Digital Wellness (DISCIPLINE)
        if tier2.get('screen_under_2h'): 
            total_points += 15
            stat_xp['discipline'] += 15
        elif tier2.get('screen_2_4h'): 
            total_points += 5
            stat_xp['discipline'] += 5
        if tier2.get('no_phone_morning'): 
            total_points += 5
            stat_xp['discipline'] += 5
        if tier2.get('no_phone_night'): 
            total_points += 5
            stat_xp['discipline'] += 5
        
        # Life Admin (ENERGY)
        if tier2.get('plan_tomorrow'): 
            total_points += 3
            stat_xp['energy'] += 3
        if tier2.get('organize_space'): 
            total_points += 8
            stat_xp['energy'] += 8
        if tier2.get('budget_review'): 
            total_points += 5
            stat_xp['energy'] += 5
        
        # Mindfulness (ENERGY)
        if tier2.get('meditation'): 
            total_points += 8
            stat_xp['energy'] += 8
        if tier2.get('gratitude'): 
            total_points += 3
            stat_xp['energy'] += 3
        if tier2.get('breathwork'): 
            total_points += 4
            stat_xp['energy'] += 4
        if tier2.get('nature_walk'): 
            total_points += 10
            stat_xp['energy'] += 10
        
        # Creative Output (INFLUENCE)
        if tier2.get('code_project'): 
            total_points += 20
            stat_xp['influence'] += 20
        if tier2.get('write_docs'): 
            total_points += 10
            stat_xp['influence'] += 10
        if tier2.get('build_design'): 
            total_points += 15
            stat_xp['influence'] += 15
        if tier2.get('open_source'): 
            total_points += 25
            stat_xp['influence'] += 25
        
        # Social & Contribution (INFLUENCE)
        if tier2.get('meaningful_conversation'): 
            total_points += 8
            stat_xp['influence'] += 8
        if tier2.get('help_someone_code'): 
            total_points += 10
            stat_xp['influence'] += 10
        if tier2.get('call_family'): 
            total_points += 5
            stat_xp['influence'] += 5
        if tier2.get('help_someone'): 
            total_points += 3
            stat_xp['influence'] += 3
        if tier2.get('teach_someone'): 
            total_points += 6
            stat_xp['influence'] += 6
        if tier2.get('give_advice'): 
            total_points += 5
            stat_xp['influence'] += 5
        if tier2.get('active_listening'): 
            total_points += 4
            stat_xp['influence'] += 4
        if tier2.get('encourage_someone'): 
            total_points += 3
            stat_xp['influence'] += 3
        if tier2.get('group_activity'): 
            total_points += 7
            stat_xp['influence'] += 7
        if tier2.get('mentor_session'): 
            total_points += 8
            stat_xp['influence'] += 8
        if tier2.get('networking'): 
            total_points += 6
            stat_xp['influence'] += 6
        if tier2.get('compliment_someone'): 
            total_points += 2
            stat_xp['influence'] += 2
        if tier2.get('thank_someone'): 
            total_points += 2
            stat_xp['influence'] += 2
        if tier2.get('check_in'): 
            total_points += 3
            stat_xp['influence'] += 3
        if tier2.get('quality_time'): 
            total_points += 10
            stat_xp['influence'] += 10
        
        # Tier 3 activities
        tier3 = entry.get('tier3', {})
        if tier3.get('flow_state_4h'): 
            total_points += 80
            stat_xp['intellect'] += 80
            entry['tier3_flow_state'] = True
        if tier3.get('zero_screens'): 
            total_points += 100
            stat_xp['discipline'] += 100
            entry['tier3_digital_monk'] = True
        if tier3.get('complete_todo'): 
            total_points += 50
            stat_xp['discipline'] += 50
        if tier3.get('cold_exposure'): 
            total_points += 30
            stat_xp['energy'] += 30
        if tier3.get('new_algorithm'): 
            total_points += 60
            stat_xp['intellect'] += 60
        if tier3.get('teach_code'): 
            total_points += 40
            stat_xp['influence'] += 40
        
        # Update streaks and add streak points
        streaks_completed = entry.get('streaks_completed', [])
        for streak_name in streaks_completed:
            if streak_name in data['streaks']:
                streak = data['streaks'][streak_name]
                
                # Check if this is consecutive day
                if streak['last_date'] == (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'):
                    streak['current'] += 1
                else:
                    streak['current'] = 1
                
                streak['last_date'] = today
                if streak['current'] > streak['longest']:
                    streak['longest'] = streak['current']
                
                # Calculate streak points
                multiplier = calculate_streak_multiplier(streak['current'])
                streak['multiplier'] = multiplier
                base = streak['base_points']
                
                # Add daily bonus for no_porn
                if streak_name == 'no_porn':
                    bonus = streak.get('daily_bonus', 2) * (streak['current'] - 1)
                    streak_points = int((base + bonus) * multiplier)
                else:
                    streak_points = int(base * multiplier)
                
                total_points += streak_points
                
                # Add to appropriate stat
                if streak_name in ['workout', 'sleep_7h']:
                    stat_xp['strength'] += int(streak_points * 0.5)
                    stat_xp['energy'] += int(streak_points * 0.5)
                elif streak_name in ['deep_work', 'reading', 'coding_practice']:
                    stat_xp['intellect'] += streak_points
                elif streak_name in ['no_porn', 'morning_routine', 'no_doomscroll', 'screen_time_under_2h']:
                    stat_xp['discipline'] += streak_points
                elif streak_name == 'meditation':
                    stat_xp['energy'] += streak_points
        
        # Check for all-day gaming penalty
        if entry.get('penalty_gaming', False):
            total_points = max(0, total_points - 15)
        
        entry['total_points'] = total_points
        entry['stat_xp'] = dict(stat_xp)
        
        # Add XP to stats
        for stat_name, xp in stat_xp.items():
            add_xp_to_stat(data, stat_name, xp)
        
        # Update character points
        data['character']['total_points'] += total_points
        data['character']['current_week_points'] += total_points
        data['skill_tree']['available_points'] += total_points
        
        # CHECK NEMESIS MODE
        nemesis_broken = check_nemesis_break(data, entry)
        if nemesis_broken:
            # Zero out points for the day
            total_points = 0
            entry['total_points'] = 0
            entry['nemesis_punishment'] = True
            
            # Increase nemesis gauge
            data['nemesis_mode']['nemesis_gauge'] = min(100, data['nemesis_mode']['nemesis_gauge'] + 10)
            data['nemesis_mode']['breaks_this_month'] += 1
            
            # Check if gauge is full
            if data['nemesis_mode']['nemesis_gauge'] >= 100:
                tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                data['nemesis_mode']['forced_rest_date'] = tomorrow
                data['nemesis_mode']['nemesis_gauge'] = 0
        
        # CHECK COMBO SYSTEM
        # Build list of all completed tier2 activities
        activities_completed = []
        for activity_name, is_done in tier2.items():
            if is_done and activity_name != 'deep_work_quality':  # Skip quality indicator
                activities_completed.append(activity_name)
        
        # Check combos across ALL logs today (merge with previous logs if exists)
        today = datetime.now().strftime('%Y-%m-%d')
        existing_entry = next((e for e in data['daily_log'] if e.get('date') == today), None)
        
        if existing_entry:
            # Merge activities from previous logs today
            existing_tier2 = existing_entry.get('tier2', {})
            for activity_name, is_done in existing_tier2.items():
                if is_done and activity_name not in activities_completed and activity_name != 'deep_work_quality':
                    activities_completed.append(activity_name)
        
        detected_combos = check_combo(activities_completed)
        combo_bonus = 0
        combo_names = []
        
        if detected_combos:
            # Award ALL detected combos (not just best one)
            for combo in detected_combos:
                combo_bonus += combo['bonus_points']
                combo_names.append(combo['name'])
            
            total_points += combo_bonus
            entry['combos_activated'] = combo_names
            entry['combo_bonus'] = combo_bonus
            
            # Update combo stats
            if 'combo_system' not in data:
                data['combo_system'] = {'total_combos': 0, 'best_combo': 0, 'all_time_bonus': 0}
            data['combo_system']['total_combos'] += len(detected_combos)
            data['combo_system']['all_time_bonus'] = data['combo_system'].get('all_time_bonus', 0) + combo_bonus
            if combo_bonus > data['combo_system'].get('best_combo', 0):
                data['combo_system']['best_combo'] = combo_bonus
        
        # Check achievements
        new_achievements = check_achievements(data, entry)
        for achievement in new_achievements:
            achievement['date_earned'] = today
            data['achievements']['earned'].append(achievement)
            data['character']['total_points'] += achievement['points_bonus']
            data['skill_tree']['available_points'] += achievement['points_bonus']
        
        # MERGE OR ADD ENTRY - Check if entry for today already exists
        existing_entry = next((e for e in data['daily_log'] if e.get('date') == today), None)
        
        if existing_entry:
            # MERGE: Combine activities from both entries
            # Merge tier2 activities (combine checkboxes)
            existing_tier2 = existing_entry.get('tier2', {})
            new_tier2 = entry.get('tier2', {})
            for activity, checked in new_tier2.items():
                if checked:  # If new entry has this activity checked
                    existing_tier2[activity] = True
            existing_entry['tier2'] = existing_tier2
            
            # Merge tier3 activities
            existing_tier3 = existing_entry.get('tier3', {})
            new_tier3 = entry.get('tier3', {})
            for activity, checked in new_tier3.items():
                if checked:
                    existing_tier3[activity] = True
            existing_entry['tier3'] = existing_tier3
            
            # Merge streaks (union of both sets)
            existing_streaks = set(existing_entry.get('streaks_completed', []))
            new_streaks = set(entry.get('streaks_completed', []))
            existing_entry['streaks_completed'] = list(existing_streaks.union(new_streaks))
            
            # Combine stat XP
            existing_stat_xp = existing_entry.get('stat_xp', {})
            new_stat_xp = entry.get('stat_xp', {})
            for stat, xp in new_stat_xp.items():
                existing_stat_xp[stat] = existing_stat_xp.get(stat, 0) + xp
            existing_entry['stat_xp'] = existing_stat_xp
            
            # Add points (not replace)
            existing_entry['total_points'] = existing_entry.get('total_points', 0) + total_points
            
            # Update tier1 if this submission completes it
            if entry.get('tier1_complete', False):
                existing_entry['tier1_complete'] = True
            
            # Update energy score (use latest)
            existing_entry['energy_score'] = entry.get('energy_score')
            
            # Append notes (don't overwrite)
            existing_notes = existing_entry.get('notes', '')
            new_notes = entry.get('notes', '')
            if new_notes:
                if existing_notes:
                    existing_entry['notes'] = existing_notes + " | " + new_notes
                else:
                    existing_entry['notes'] = new_notes
            
            # Combine combo info
            if combo_names:
                existing_combos = existing_entry.get('combos_activated', [])
                existing_combos.extend(combo_names)
                existing_entry['combos_activated'] = existing_combos
                existing_entry['combo_bonus'] = existing_entry.get('combo_bonus', 0) + combo_bonus
            
            # Track that this was an update
            existing_entry['log_count'] = existing_entry.get('log_count', 1) + 1
            existing_entry['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        else:
            # NEW ENTRY: First log of the day
            entry['log_count'] = 1
            entry['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data['daily_log'].append(entry)
        
        save_data(data)
        
        return jsonify({
            'success': True, 
            'total_points': total_points,
            'achievements': new_achievements,
            'stat_xp': dict(stat_xp),
            'merged': existing_entry is not None,
            'message': 'Activities added to today\'s log!' if existing_entry else 'New daily log created!',
            'combos_activated': combo_names if combo_names else [],
            'combo_bonus': combo_bonus
        })
    
    else:
        # Return last 30 days
        return jsonify(data['daily_log'][-30:])

@app.route('/api/skill-tree/unlock/<skill_id>', methods=['POST'])
def unlock_skill(skill_id):
    """Unlock a skill from skill tree"""
    data = load_data()
    
    skill = next((s for s in data['skill_tree']['locked'] if s['id'] == skill_id), None)
    if not skill:
        return jsonify({'success': False, 'error': 'Skill not found'}), 404
    
    if data['skill_tree']['available_points'] < skill['cost']:
        return jsonify({'success': False, 'error': 'Not enough points'}), 400
    
    # Unlock skill
    data['skill_tree']['available_points'] -= skill['cost']
    data['skill_tree']['locked'].remove(skill)
    skill['date_unlocked'] = datetime.now().strftime('%Y-%m-%d')
    data['skill_tree']['unlocked'].append(skill)
    
    save_data(data)
    
    return jsonify({'success': True, 'skill': skill})

@app.route('/api/achievements')
def get_achievements():
    """Get all achievements"""
    data = load_data()
    return jsonify(data['achievements'])

@app.route('/api/stats/weekly')
def weekly_stats():
    """Get weekly statistics"""
    data = load_data()
    
    # Get last 7 days
    if len(data['daily_log']) >= 7:
        last_week = data['daily_log'][-7:]
        total = sum(day.get('total_points', 0) for day in last_week)
        avg = total / 7
        best_day = max(last_week, key=lambda x: x.get('total_points', 0))
        worst_day = min(last_week, key=lambda x: x.get('total_points', 0))
        
        return jsonify({
            'total_points': total,
            'average_points': round(avg, 1),
            'best_day': best_day.get('total_points', 0),
            'worst_day': worst_day.get('total_points', 0),
            'target': data['weekly_targets']['target_points'],
            'on_track': total >= data['weekly_targets']['target_points']
        })
    
    return jsonify({'message': 'Not enough data yet'})

@app.route('/api/personal-records', methods=['GET', 'POST', 'DELETE'])
def personal_records():
    """Manage personal records for exercises"""
    data = load_data()
    
    if 'personal_records' not in data:
        data['personal_records'] = {'exercises': {}}
    
    if request.method == 'GET':
        return jsonify(data['personal_records'])
    
    elif request.method == 'POST':
        entry = request.json
        exercise_name = entry.get('exercise_name', '').strip()
        weight = float(entry.get('weight', 0))
        reps = int(entry.get('reps', 0))
        sets = int(entry.get('sets', 0))
        
        if not exercise_name:
            return jsonify({'success': False, 'error': 'Exercise name required'}), 400
        
        # Calculate total volume (weight × reps × sets) as the comparison metric
        new_volume = weight * reps * sets
        
        # Check if this is a new PR
        is_pr = False
        points_earned = 0
        old_volume = 0
        improvement_percent = 0
        
        if exercise_name in data['personal_records']['exercises']:
            old_record = data['personal_records']['exercises'][exercise_name]
            old_volume = old_record['weight'] * old_record['reps'] * old_record['sets']
            
            if new_volume > old_volume:
                is_pr = True
                improvement_percent = ((new_volume - old_volume) / old_volume) * 100
                
                # Award points based on improvement
                if improvement_percent >= 20:
                    points_earned = 8
                elif improvement_percent >= 10:
                    points_earned = 7
                elif improvement_percent >= 5:
                    points_earned = 6
                else:
                    points_earned = 5
                
                # Update the PR
                data['personal_records']['exercises'][exercise_name] = {
                    'weight': weight,
                    'reps': reps,
                    'sets': sets,
                    'volume': new_volume,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'previous_volume': old_volume
                }
                
                # Add points to character
                data['character']['total_points'] += points_earned
                data['character']['current_week_points'] += points_earned
                data['skill_tree']['available_points'] += points_earned
                
                # Add XP to STRENGTH
                add_xp_to_stat(data, 'strength', points_earned)
                
        else:
            # First time logging this exercise - it's automatically a PR
            is_pr = True
            points_earned = 5  # Base points for first PR
            
            data['personal_records']['exercises'][exercise_name] = {
                'weight': weight,
                'reps': reps,
                'sets': sets,
                'volume': new_volume,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'previous_volume': 0
            }
            
            # Add points to character
            data['character']['total_points'] += points_earned
            data['character']['current_week_points'] += points_earned
            data['skill_tree']['available_points'] += points_earned
            
            # Add XP to STRENGTH
            add_xp_to_stat(data, 'strength', points_earned)
        
        save_data(data)
        
        return jsonify({
            'success': True,
            'is_pr': is_pr,
            'points_earned': points_earned,
            'improvement_percent': round(improvement_percent, 1),
            'new_volume': new_volume,
            'old_volume': old_volume,
            'exercise': data['personal_records']['exercises'][exercise_name]
        })
    
    elif request.method == 'DELETE':
        exercise_name = request.json.get('exercise_name')
        
        if exercise_name in data['personal_records']['exercises']:
            del data['personal_records']['exercises'][exercise_name]
            save_data(data)
            return jsonify({'success': True, 'message': f'Deleted PR for {exercise_name}'})
        
        return jsonify({'success': False, 'error': 'Exercise not found'}), 404

@app.route('/api/export')
def export_data():
    """Export all data as JSON"""
    data = load_data()
    return jsonify(data)

@app.route('/api/notes', methods=['GET', 'POST', 'DELETE'])
def notes():
    """Manage notes and plans"""
    data = load_data()
    
    if 'notes' not in data:
        data['notes'] = {'daily_notes': [], 'plans': []}
    
    if request.method == 'GET':
        # Return last 30 notes and active plans
        recent_notes = data['notes']['daily_notes'][-30:] if data['notes']['daily_notes'] else []
        active_plans = [p for p in data['notes']['plans'] if not p.get('completed', False)]
        
        return jsonify({
            'daily_notes': recent_notes,
            'plans': active_plans,
            'all_plans': data['notes']['plans']
        })
    
    elif request.method == 'POST':
        entry = request.json
        note_type = entry.get('type')  # 'daily_note', 'tomorrow_plan', 'goal', 'idea'
        content = entry.get('content', '').strip()
        category = entry.get('category', 'general')
        
        if not content:
            return jsonify({'success': False, 'error': 'Content required'}), 400
        
        points_earned = 0
        today = datetime.now().strftime('%Y-%m-%d')
        
        if note_type == 'daily_note':
            # Daily reflection/journal entry - 2 points
            points_earned = 2
            
            note = {
                'id': len(data['notes']['daily_notes']) + 1,
                'content': content,
                'category': category,
                'date': today,
                'type': 'daily_note'
            }
            data['notes']['daily_notes'].append(note)
            
        elif note_type == 'tomorrow_plan':
            # Tomorrow's plan - 5 points
            points_earned = 5
            
            plan = {
                'id': len(data['notes']['plans']) + 1,
                'content': content,
                'category': category,
                'created_date': today,
                'target_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'completed': False,
                'type': 'tomorrow_plan'
            }
            data['notes']['plans'].append(plan)
            
        elif note_type == 'goal':
            # Long-term goal - 3 points
            points_earned = 3
            
            plan = {
                'id': len(data['notes']['plans']) + 1,
                'content': content,
                'category': category,
                'created_date': today,
                'target_date': entry.get('target_date'),
                'completed': False,
                'type': 'goal'
            }
            data['notes']['plans'].append(plan)
            
        elif note_type == 'idea':
            # Quick idea capture - 1 point
            points_earned = 1
            
            note = {
                'id': len(data['notes']['daily_notes']) + 1,
                'content': content,
                'category': category,
                'date': today,
                'type': 'idea'
            }
            data['notes']['daily_notes'].append(note)
        
        # Award points
        if points_earned > 0:
            data['character']['total_points'] += points_earned
            data['character']['current_week_points'] += points_earned
            data['skill_tree']['available_points'] += points_earned
            
            # Add XP to DISCIPLINE (planning) or ENERGY (reflection)
            if note_type in ['tomorrow_plan', 'goal']:
                add_xp_to_stat(data, 'discipline', points_earned)
            else:
                add_xp_to_stat(data, 'energy', points_earned)
        
        save_data(data)
        
        return jsonify({
            'success': True,
            'points_earned': points_earned,
            'note_type': note_type
        })
    
    elif request.method == 'DELETE':
        item_id = request.json.get('id')
        item_type = request.json.get('type')
        
        if item_type == 'note':
            data['notes']['daily_notes'] = [n for n in data['notes']['daily_notes'] if n.get('id') != item_id]
        elif item_type == 'plan':
            data['notes']['plans'] = [p for p in data['notes']['plans'] if p.get('id') != item_id]
        
        save_data(data)
        return jsonify({'success': True, 'message': 'Deleted successfully'})

@app.route('/api/notes/complete-plan/<int:plan_id>', methods=['POST'])
def complete_plan(plan_id):
    """Mark a plan as completed"""
    data = load_data()
    
    plan = next((p for p in data['notes']['plans'] if p.get('id') == plan_id), None)
    
    if not plan:
        return jsonify({'success': False, 'error': 'Plan not found'}), 404
    
    if plan.get('completed'):
        return jsonify({'success': False, 'error': 'Plan already completed'}), 400
    
    # Mark as completed
    plan['completed'] = True
    plan['completed_date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Award bonus points for completing plans
    bonus_points = 3 if plan['type'] == 'tomorrow_plan' else 5
    
    data['character']['total_points'] += bonus_points
    data['character']['current_week_points'] += bonus_points
    data['skill_tree']['available_points'] += bonus_points
    add_xp_to_stat(data, 'discipline', bonus_points)
    
    save_data(data)
    
    return jsonify({
        'success': True,
        'bonus_points': bonus_points,
        'plan': plan
    })

@app.route('/api/daily-challenge')
def get_daily_challenge():
    """Get or generate today's daily challenge"""
    data = load_data()
    
    if 'daily_challenge' not in data:
        data['daily_challenge'] = {'current_challenge': None, 'date': '', 'completed': False, 'history': []}
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Generate new challenge if date changed or no challenge exists
    if data['daily_challenge']['date'] != today or not data['daily_challenge']['current_challenge']:
        challenge = generate_daily_challenge()
        data['daily_challenge']['current_challenge'] = challenge
        data['daily_challenge']['date'] = today
        data['daily_challenge']['completed'] = False
        save_data(data)
    
    return jsonify(data['daily_challenge'])

@app.route('/api/daily-challenge/complete', methods=['POST'])
def complete_daily_challenge():
    """Mark daily challenge as complete"""
    data = load_data()
    
    if not data['daily_challenge'].get('completed', False):
        challenge = data['daily_challenge']['current_challenge']
        points = challenge['points']
        
        # Award points
        data['character']['total_points'] += points
        data['character']['current_week_points'] += points
        data['skill_tree']['available_points'] += points
        
        # Add XP to appropriate stat
        category_to_stat = {
            'strength': 'strength',
            'intellect': 'intellect',
            'discipline': 'discipline',
            'energy': 'energy',
            'influence': 'influence'
        }
        stat = category_to_stat.get(challenge['category'], 'discipline')
        add_xp_to_stat(data, stat, points)
        
        # Mark as completed
        data['daily_challenge']['completed'] = True
        
        # Add to history
        data['daily_challenge']['history'].append({
            'challenge': challenge,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'completed': True
        })
        
        save_data(data)
        
        return jsonify({
            'success': True,
            'points_earned': points,
            'challenge': challenge
        })
    
    return jsonify({'success': False, 'error': 'Challenge already completed today'})

@app.route('/api/nemesis-mode', methods=['GET', 'POST'])
def nemesis_mode():
    """Manage nemesis mode settings"""
    data = load_data()
    
    if 'nemesis_mode' not in data:
        data['nemesis_mode'] = {
            'active': False,
            'non_negotiables': [],
            'nemesis_gauge': 0,
            'breaks_this_month': 0,
            'forced_rest_date': None
        }
    
    if request.method == 'GET':
        return jsonify(data['nemesis_mode'])
    
    elif request.method == 'POST':
        action = request.json.get('action')
        
        if action == 'activate':
            non_negotiables = request.json.get('non_negotiables', [])
            if len(non_negotiables) != 3:
                return jsonify({'success': False, 'error': 'Must select exactly 3 non-negotiables'}), 400
            
            data['nemesis_mode']['active'] = True
            data['nemesis_mode']['non_negotiables'] = non_negotiables
            save_data(data)
            
            return jsonify({'success': True, 'message': 'Nemesis Mode activated!'})
        
        elif action == 'deactivate':
            data['nemesis_mode']['active'] = False
            save_data(data)
            
            return jsonify({'success': True, 'message': 'Nemesis Mode deactivated'})
    
    return jsonify(data['nemesis_mode'])

@app.route('/api/analytics')
def get_analytics():
    """Get analytics and statistics"""
    data = load_data()
    
    daily_log = data.get('daily_log', [])
    
    if len(daily_log) == 0:
        return jsonify({
            'total_days': 0,
            'average_points': 0,
            'best_day': 0,
            'worst_day': 0,
            'streak_data': {},
            'activity_breakdown': {},
            'weekly_trend': []
        })
    
    # Calculate statistics
    points_list = [entry.get('total_points', 0) for entry in daily_log]
    
    # Activity breakdown
    activity_breakdown = {}
    for entry in daily_log:
        tier2 = entry.get('tier2', {})
        for activity, done in tier2.items():
            if done:
                activity_breakdown[activity] = activity_breakdown.get(activity, 0) + 1
    
    # Weekly trend (last 4 weeks)
    weekly_trend = []
    if len(daily_log) >= 7:
        for i in range(min(4, len(daily_log) // 7)):
            week_start = -(i + 1) * 7
            week_end = -i * 7 if i > 0 else None
            week_data = daily_log[week_start:week_end]
            week_points = sum(entry.get('total_points', 0) for entry in week_data)
            weekly_trend.insert(0, {
                'week': i + 1,
                'points': week_points,
                'avg': round(week_points / len(week_data), 1)
            })
    
    # Day of week analysis
    day_of_week_points = {}
    for entry in daily_log:
        date_str = entry.get('date')
        if date_str:
            day = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
            points = entry.get('total_points', 0)
            if day not in day_of_week_points:
                day_of_week_points[day] = []
            day_of_week_points[day].append(points)
    
    day_averages = {day: round(sum(points) / len(points), 1) 
                    for day, points in day_of_week_points.items()}
    best_day_of_week = max(day_averages.items(), key=lambda x: x[1])[0] if day_averages else None
    
    analytics_data = {
        'total_days': len(daily_log),
        'average_points': round(sum(points_list) / len(points_list), 1),
        'best_day': max(points_list),
        'worst_day': min(points_list),
        'total_points': sum(points_list),
        'activity_breakdown': activity_breakdown,
        'weekly_trend': weekly_trend,
        'best_day_of_week': best_day_of_week,
        'day_averages': day_averages,
        'streak_data': data.get('streaks', {})
    }
    
    return jsonify(analytics_data)

@app.route('/api/ghost-data')
def get_ghost_data():
    """Get ghost/comparison data"""
    data = load_data()
    
    daily_log = data.get('daily_log', [])
    
    if len(daily_log) < 7:
        return jsonify({
            'has_ghost': False,
            'message': 'Need at least 7 days of data to generate ghost'
        })
    
    # Calculate weekly average
    recent_week = daily_log[-7:]
    weekly_avg = sum(entry.get('total_points', 0) for entry in recent_week) / 7
    
    # Get best week
    best_week_points = 0
    if len(daily_log) >= 14:
        for i in range(len(daily_log) - 6):
            week = daily_log[i:i+7]
            week_points = sum(entry.get('total_points', 0) for entry in week)
            if week_points > best_week_points:
                best_week_points = week_points
    
    # Compare today vs past self
    today = datetime.now().strftime('%Y-%m-%d')
    today_entry = next((e for e in daily_log if e.get('date') == today), None)
    today_points = today_entry.get('total_points', 0) if today_entry else 0
    
    # Get same day last week
    last_week_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    last_week_entry = next((e for e in daily_log if e.get('date') == last_week_date), None)
    last_week_points = last_week_entry.get('total_points', 0) if last_week_entry else 0
    
    ghost_data = {
        'has_ghost': True,
        'weekly_average': round(weekly_avg, 1),
        'best_week': best_week_points,
        'today_vs_last_week': {
            'today': today_points,
            'last_week': last_week_points,
            'difference': today_points - last_week_points,
            'winning': today_points > last_week_points
        },
        'total_days': len(daily_log)
    }
    
    return jsonify(ghost_data)

@app.route('/api/budget', methods=['GET', 'POST'])
def budget_tracker():
    """Manage budget and transactions"""
    data = load_data()
    
    if 'budget_tracker' not in data:
        data['budget_tracker'] = {
            'current_balance': 0,
            'transactions': [],
            'categories': {
                'income': ["Salary", "Freelance", "Gifts", "Other Income"],
                'expenses': ["Food", "Transport", "Entertainment", "Fitness", "Learning", "Bills", "Shopping", "Other"]
            },
            'monthly_budget': {},
            'monthly_summary': []
        }
    
    if request.method == 'GET':
        today = datetime.now()
        current_month = today.strftime('%Y-%m')
        
        monthly_income = 0
        monthly_expenses = 0
        category_spending = {}
        
        for transaction in data['budget_tracker']['transactions']:
            trans_date = transaction.get('date', '')
            if trans_date.startswith(current_month):
                amount = transaction['amount']
                category = transaction['category']
                
                if transaction['type'] == 'income':
                    monthly_income += amount
                else:
                    monthly_expenses += amount
                    category_spending[category] = category_spending.get(category, 0) + amount
        
        return jsonify({
            'balance': data['budget_tracker']['current_balance'],
            'transactions': data['budget_tracker']['transactions'][-50:],
            'monthly_budget': data['budget_tracker']['monthly_budget'],
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'category_spending': category_spending,
            'categories': data['budget_tracker']['categories']
        })
    
    elif request.method == 'POST':
        action = request.json.get('action')
        
        if action == 'add_transaction':
            transaction = {
                'id': len(data['budget_tracker']['transactions']) + 1,
                'type': request.json.get('type'),
                'amount': float(request.json.get('amount')),
                'category': request.json.get('category'),
                'description': request.json.get('description', ''),
                'date': request.json.get('date', datetime.now().strftime('%Y-%m-%d'))
            }
            
            if transaction['type'] == 'income':
                data['budget_tracker']['current_balance'] += transaction['amount']
            else:
                data['budget_tracker']['current_balance'] -= transaction['amount']
            
            data['budget_tracker']['transactions'].append(transaction)
            
            points = 2
            data['character']['total_points'] += points
            data['skill_tree']['available_points'] += points
            add_xp_to_stat(data, 'discipline', points)
            
            save_data(data)
            
            return jsonify({
                'success': True,
                'transaction': transaction,
                'new_balance': data['budget_tracker']['current_balance'],
                'points_earned': points
            })
        
        elif action == 'set_budget':
            budgets = request.json.get('budgets', {})
            data['budget_tracker']['monthly_budget'] = budgets
            save_data(data)
            return jsonify({'success': True, 'message': 'Budget updated'})
        
        elif action == 'delete_transaction':
            trans_id = request.json.get('id')
            transaction = next((t for t in data['budget_tracker']['transactions'] if t['id'] == trans_id), None)
            
            if transaction:
                if transaction['type'] == 'income':
                    data['budget_tracker']['current_balance'] -= transaction['amount']
                else:
                    data['budget_tracker']['current_balance'] += transaction['amount']
                
                data['budget_tracker']['transactions'].remove(transaction)
                save_data(data)
                return jsonify({'success': True, 'message': 'Transaction deleted'})
            
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404

@app.route('/api/workouts', methods=['GET', 'POST', 'DELETE'])
def workout_sessions():
    """Manage workout templates and sessions"""
    data = load_data()
    
    if 'workout_sessions' not in data:
        data['workout_sessions'] = {'templates': {}, 'history': []}
    
    if request.method == 'GET':
        return jsonify({
            'templates': data['workout_sessions']['templates'],
            'history': data['workout_sessions']['history'][-30:]
        })
    
    elif request.method == 'POST':
        action = request.json.get('action')
        
        if action == 'create_template':
            template = {
                'id': request.json.get('id'),
                'name': request.json.get('name'),
                'day': request.json.get('day'),
                'exercises': request.json.get('exercises', [])
            }
            
            data['workout_sessions']['templates'][template['id']] = template
            save_data(data)
            return jsonify({'success': True, 'template': template})
        
        elif action == 'log_session':
            session = {
                'id': len(data['workout_sessions']['history']) + 1,
                'template_id': request.json.get('template_id'),
                'template_name': request.json.get('template_name'),
                'date': request.json.get('date', datetime.now().strftime('%Y-%m-%d')),
                'exercises_completed': request.json.get('exercises_completed', []),
                'duration_minutes': request.json.get('duration_minutes', 0),
                'notes': request.json.get('notes', '')
            }
            
            data['workout_sessions']['history'].append(session)
            
            base_points = 25
            bonus = min(len(session['exercises_completed']) * 2, 15)
            total = base_points + bonus
            
            data['character']['total_points'] += total
            data['skill_tree']['available_points'] += total
            add_xp_to_stat(data, 'strength', total)
            
            save_data(data)
            
            return jsonify({
                'success': True,
                'session': session,
                'points_earned': total
            })
        
        elif action == 'update_template':
            template_id = request.json.get('id')
            if template_id in data['workout_sessions']['templates']:
                data['workout_sessions']['templates'][template_id] = {
                    'id': template_id,
                    'name': request.json.get('name'),
                    'day': request.json.get('day'),
                    'exercises': request.json.get('exercises', [])
                }
                save_data(data)
                return jsonify({'success': True})
            
            return jsonify({'success': False, 'error': 'Template not found'}), 404
    
    elif request.method == 'DELETE':
        template_id = request.json.get('id')
        if template_id in data['workout_sessions']['templates']:
            del data['workout_sessions']['templates'][template_id]
            save_data(data)
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Template not found'}), 404

@app.route('/api/reset', methods=['POST'])
def reset_data():
    """Reset all data (use with caution)"""
    data = init_data()
    save_data(data)
    return jsonify({'success': True, 'message': 'All data reset'})

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Initialize data if doesn't exist
    if not os.path.exists(DATA_FILE):
        init_data()
    
    print("🎮 Warrior Dashboard Starting...")
    print("📊 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
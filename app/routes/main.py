"""Main Routes — Warrior Dashboard
================================
Architecture:
    CharacterRepository  — all DB access
    BaseService          — shared character + save logic (inherited by all services)
    InventoryService     — extends BaseService for list-based JSON columns
    Feature services     — ChallengeService, SkillTreeService, NoteService, etc.
    DashboardBuilder     — assembles index template context
    Routes               — thin wrappers; no business logic
"""
 
import random
import traceback
from copy import deepcopy
from datetime import datetime, timedelta
 
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm.attributes import flag_modified
 
from app.models import Character, DailyLog, User, db
from app.features.character_init import init_character_data, init_streaks
from app.features.combos import calculate_combo_bonus, check_combos
from app.features.leveling import calculate_level_up
from app.features.points import calculate_activity_points, calculate_tier1_points
from app.features.stats import calculate_stat_xp, update_stats
from app.features.streaks import update_streaks
 
bp = Blueprint('main', __name__)
 
 
# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════
 
DEFAULT_STATS = {
    'body': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
    'mind': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
    'soul': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
}
 
SKILL_TREE_ITEMS = [
    {'id': 'advanced_workout',   'name': 'Advanced Workout Program',    'cost': 500,  'category': 'body'},
    {'id': 'premium_learning',   'name': 'Premium Learning Platform',   'cost': 500,  'category': 'mind'},
    {'id': 'coding_course',      'name': 'Advanced Programming Course', 'cost': 500,  'category': 'mind'},
    {'id': 'project_equipment',  'name': 'New Dev Equipment/Tools',     'cost': 500,  'category': 'soul'},
    {'id': 'cheat_day',          'name': 'Guilt-Free Rest Day',         'cost': 500,  'category': 'body'},
    {'id': 'weekend_trip',       'name': 'Weekend Experience/Trip',     'cost': 1000, 'category': 'body'},
    {'id': 'mentor_session_rew', 'name': 'Mentor/Coach Session',        'cost': 1000, 'category': 'soul'},
    {'id': 'dream_purchase',     'name': 'Major Dream Purchase',        'cost': 2500, 'category': 'soul'},
    {'id': 'certification',      'name': 'Professional Certification',  'cost': 2500, 'category': 'mind'},
]
 
DAILY_CHALLENGES = [
    {'id': 'no_caffeine',        'name': 'No Caffeine Today',          'description': 'No coffee, tea, or energy drinks',   'points': 15, 'category': 'body'},
    {'id': 'read_1h',            'name': 'Read for 1 Hour Straight',   'description': 'No breaks, full focus reading',       'points': 20, 'category': 'mind'},
    {'id': 'ice_bath',           'name': '10-Minute Cold Shower',      'description': 'Cold exposure challenge',             'points': 30, 'category': 'body'},
    {'id': 'teach_someone',      'name': 'Teach Someone Something',    'description': 'Share knowledge with another person', 'points': 25, 'category': 'soul'},
    {'id': 'no_social_media',    'name': 'Zero Social Media',          'description': 'Not even a peek',                    'points': 20, 'category': 'mind'},
    {'id': 'wake_5am',           'name': 'Wake Up at 5 AM',            'description': 'Early bird special',                 'points': 15, 'category': 'mind'},
    {'id': '100_burpees',        'name': '100 Burpees',                'description': 'All at once or throughout day',       'points': 25, 'category': 'body'},
    {'id': 'no_screens_evening', 'name': 'No Screens After 8 PM',      'description': 'Evening digital detox',              'points': 15, 'category': 'body'},
    {'id': 'help_stranger',      'name': 'Help a Stranger',            'description': 'Random act of kindness',             'points': 20, 'category': 'soul'},
    {'id': '30min_meditation',   'name': '30-Minute Meditation',       'description': 'Extended mindfulness session',        'points': 25, 'category': 'body'},
    {'id': 'no_sugar',           'name': 'No Sugar Today',             'description': 'Zero added sugars',                  'points': 15, 'category': 'body'},
    {'id': 'learn_new_concept',  'name': 'Learn Something New',        'description': 'Outside your comfort zone',          'points': 20, 'category': 'mind'},
    {'id': 'write_1000_words',   'name': 'Write 1000 Words',           'description': 'Journal, blog, or creative writing', 'points': 20, 'category': 'mind'},
    {'id': 'no_complaints',      'name': "Don't Complain All Day",     'description': 'Catch yourself, stay positive',      'points': 15, 'category': 'mind'},
    {'id': 'silent_workout',     'name': 'No Music During Workout',    'description': 'Pure focus, no audio',               'points': 10, 'category': 'mind'},
]
 
ACHIEVEMENTS_LIST = [
    {'id': 'week_warrior',  'name': 'Week Warrior',      'description': '7 days of 100+ points',               'points_bonus': 50},
    {'id': 'balanced_life', 'name': 'Balanced Life',     'description': 'Hit all 3 stat categories in a week', 'points_bonus': 50},
    {'id': 'comeback_kid',  'name': 'Comeback Kid',      'description': '200+ points after a <50p day',        'points_bonus': 30},
    {'id': 'flow_state',    'name': 'Flow State Master', 'description': '4+ hours deep work in one day',       'points_bonus': 80},
    {'id': 'digital_monk',  'name': 'Digital Monk',      'description': 'Zero screens entire day',             'points_bonus': 100},
    {'id': 'streak_legend', 'name': 'Streak Legend',     'description': '30-day streak on any activity',       'points_bonus': 100},
]
 
TIER2_ACTIVITIES = [
    'full_workout', 'light_exercise', 'stretching', 'cold_shower',
    'deep_work', 'read_book', 'code_practice', 'meditation',
    'push_ups_100', 'steps_10k', 'study_pomodoro', 'project_dev',
    'part_time_job', 'new_skill', 'kinnu', 'online_course', 'journal',
    'screen_under_2h', 'screen_2_4h', 'no_phone_morning', 'no_phone_night',
    'plan_tomorrow', 'organize_space', 'budget_review',
    'gratitude', 'breathwork', 'nature_walk',
    'code_project', 'write_docs', 'build_design', 'open_source',
    'meaningful_conversation', 'help_someone_code', 'call_family',
    'help_someone', 'teach_someone', 'give_advice', 'active_listening',
    'encourage_someone', 'group_activity', 'networking',
    'compliment_someone', 'thank_someone', 'check_in', 'quality_time',
]
 
TIER3_ACTIVITIES = [
    'flow_state_4h', 'zero_screens', 'complete_todo',
    'cold_exposure', 'new_algorithm', 'teach_code',
]
 
STREAK_NAMES = [
    'no_porn', 'workout', 'meditation', 'deep_work', 'reading',
    'coding_practice', 'sleep_7h', 'morning_routine',
    'no_doomscroll', 'screen_time_under_2h',
]
 
ONBOARD_FOCUS_XP = {
    'body': {'body': 20, 'mind': 0,  'soul': 0},
    'mind': {'body': 0,  'mind': 20, 'soul': 0},
    'soul': {'body': 0,  'mind': 0,  'soul': 20},
    'all':  {'body': 10, 'mind': 10, 'soul': 10},
}
 
ONBOARD_PRIORITY_TASKS = {
    'body': ['full_workout', 'steps_10k', 'cold_shower', 'meditation', 'stretching'],
    'mind': ['deep_work', 'study_pomodoro', 'code_practice', 'read_book', 'plan_tomorrow'],
    'soul': ['meaningful_conversation', 'call_family', 'quality_time', 'group_activity', 'networking'],
    'all':  ['full_workout', 'deep_work', 'meaningful_conversation', 'meditation', 'plan_tomorrow'],
}
 
ONBOARD_OBSTACLE_STREAKS = {
    'consistency': 'morning_routine',
    'motivation':  'no_doomscroll',
    'time':        'deep_work',
    'habits':      'meditation',
}
 
 
# ══════════════════════════════════════════════════════════════════════════════
# Repository — all database access lives here
# ══════════════════════════════════════════════════════════════════════════════
 
class CharacterRepository:
    """Handles all DB reads and writes for the Character model."""
 
    @staticmethod
    def get_or_create(user_id: int) -> Character:
        character = Character.query.filter_by(user_id=user_id).first()
 
        if not character:
            character = Character(
                user_id=user_id,
                stats=init_character_data()['stats'],
                streaks=init_streaks(),
            )
            db.session.add(character)
            db.session.commit()
 
        if not character.stats or not isinstance(character.stats, dict):
            character.stats = init_character_data()['stats']
            db.session.commit()
 
        return character
 
    @staticmethod
    def save(character: Character) -> None:
        """Force SQLAlchemy to detect all JSON mutations before committing."""
        json_columns = [
            'stats', 'streaks', 'achievements', 'skill_tree',
            'daily_challenge', 'notes', 'plans',
            'nemesis_mode', 'budget', 'prog_skills',
        ]
        for column in json_columns:
            value = getattr(character, column, None)
            if value is not None:
                setattr(character, column, deepcopy(value))
                flag_modified(character, column)
 
        db.session.commit()
 
    @staticmethod
    def get_logs(user_id: int, limit: int = None, order: str = 'desc') -> list:
        query = DailyLog.query.filter_by(user_id=user_id)
        query = query.order_by(DailyLog.date.desc() if order == 'desc' else DailyLog.date.asc())
        return query.limit(limit).all() if limit else query.all()
 
 
# ══════════════════════════════════════════════════════════════════════════════
# Base service — all feature services inherit from this
# ══════════════════════════════════════════════════════════════════════════════
 
class BaseService:
    """
    Provides every feature service with a character instance and a save method.
    All feature services inherit from this class.
    """
 
    def __init__(self, character: Character):
        self.character = character
 
    def save(self) -> None:
        CharacterRepository.save(self.character)
 
    def _add_points(self, points: int, stat: str = None) -> None:
        """Add points to total and optionally grant XP to a stat."""
        self.character.total_points        += points
        self.character.current_week_points += points
        self.character.level = calculate_level_up(self.character.total_points)
        if stat:
            self.character.stats = update_stats(self.character.stats or {}, {stat: points})
 
 
# ══════════════════════════════════════════════════════════════════════════════
# Inventory service — base for services managing list-based JSON columns
# ══════════════════════════════════════════════════════════════════════════════
 
class InventoryService(BaseService):
    """
    Extends BaseService with helpers for reading and writing list-based JSON
    columns (notes, plans, workout history, transactions, etc.).
 
    Subclasses call _get_list / _set_list instead of touching the character
    JSON columns directly — mutations are handled in one place.
    """
 
    def _get_list(self, column: str) -> list:
        return list(getattr(self.character, column) or [])
 
    def _set_list(self, column: str, data: list) -> None:
        setattr(self.character, column, data)
        flag_modified(self.character, column)
 
    def _get_dict(self, column: str) -> dict:
        return dict(getattr(self.character, column) or {})
 
    def _set_dict(self, column: str, data: dict) -> None:
        setattr(self.character, column, data)
        flag_modified(self.character, column)
 
 
# ══════════════════════════════════════════════════════════════════════════════
# Feature services
# ══════════════════════════════════════════════════════════════════════════════
 
class ChallengeService(BaseService):
    """Manages the daily challenge — assigns one per day and marks completion."""
 
    TODAY = datetime.now().strftime('%Y-%m-%d')
 
    def get_today(self) -> dict:
        challenge_data = self.character.daily_challenge or {}
 
        if challenge_data.get('date') != self.TODAY:
            challenge_data = {
                'date':      self.TODAY,
                'challenge': random.choice(DAILY_CHALLENGES),
                'completed': False,
            }
            self.character.daily_challenge = deepcopy(challenge_data)
            flag_modified(self.character, 'daily_challenge')
            db.session.commit()
 
        return challenge_data
 
    def complete(self) -> int:
        """Mark today's challenge as done and return points earned."""
        challenge_data = self.character.daily_challenge or {}
 
        if challenge_data.get('date') != self.TODAY:
            raise ValueError('No challenge assigned for today.')
        if challenge_data.get('completed'):
            raise ValueError('Challenge already completed today.')
 
        challenge = challenge_data['challenge']
        points    = challenge['points']
 
        challenge_data['completed']        = True
        self.character.daily_challenge     = deepcopy(challenge_data)
        self._add_points(points, stat=challenge.get('category', 'mind'))
        self.save()
 
        return points
 
 
class SkillTreeService(BaseService):
    """Handles reading the skill tree and unlocking new skills."""
 
    def get_locked(self) -> list:
        unlocked_ids = self._get_unlocked_ids()
        return [s for s in SKILL_TREE_ITEMS if s['id'] not in unlocked_ids]
 
    def get_unlocked(self) -> list:
        tree = self.character.skill_tree or {}
        return tree.get('unlocked', [])
 
    def unlock(self, skill_id: str) -> dict:
        """Unlock a skill. Raises ValueError if not found or unaffordable."""
        skill = next((s for s in SKILL_TREE_ITEMS if s['id'] == skill_id), None)
 
        if not skill:
            raise ValueError('Skill not found.')
        if self.character.total_points < skill['cost']:
            raise ValueError(f"Need {skill['cost']}p — you have {self.character.total_points}p.")
        if skill_id in self._get_unlocked_ids():
            raise ValueError('Already unlocked.')
 
        tree     = dict(self.character.skill_tree or {'unlocked': []})
        unlocked = list(tree.get('unlocked', []))
        unlocked.append({**skill, 'date_unlocked': datetime.now().strftime('%Y-%m-%d')})
        tree['unlocked']          = unlocked
        self.character.skill_tree = deepcopy(tree)
        self.character.total_points -= skill['cost']
        self.save()
 
        return skill
 
    def _get_unlocked_ids(self) -> list:
        tree = self.character.skill_tree or {}
        return [s['id'] for s in tree.get('unlocked', [])]
 
 
class AchievementService(BaseService):
    """Checks conditions and grants achievements."""
 
    def check_all(self, recent_logs: list) -> None:
        points_list = [log.total_points for log in recent_logs]
        earned_ids  = [a['id'] for a in (self.character.achievements or [])]
 
        if 'week_warrior' not in earned_ids and len(points_list) >= 7:
            if all(p >= 100 for p in points_list[:7]):
                self._grant('week_warrior')
 
        if 'streak_legend' not in earned_ids:
            for streak in (self.character.streaks or {}).values():
                if isinstance(streak, dict) and streak.get('current', 0) >= 30:
                    self._grant('streak_legend')
                    break
 
    def _grant(self, achievement_id: str) -> None:
        match = next((a for a in ACHIEVEMENTS_LIST if a['id'] == achievement_id), None)
        if not match:
            return
 
        earned = list(self.character.achievements or [])
        earned.append({**match, 'date_earned': datetime.now().strftime('%Y-%m-%d')})
        self.character.achievements  = earned
        self.character.total_points += match['points_bonus']
        flag_modified(self.character, 'achievements')
        flash(f"🏆 Achievement: {match['name']}! +{match['points_bonus']}p", 'success')
 
 
class NoteService(InventoryService):
    """Manages notes and plans stored on the character."""
 
    def add_note(self, content: str) -> int:
        """Save a journal note. Returns points earned."""
        notes = self._get_list('notes')
        notes.append({'id': len(notes) + 1, 'content': content,
                      'date': datetime.now().strftime('%Y-%m-%d')})
        self._set_list('notes', notes[-50:])
        self._add_points(2, stat='mind')
        self.save()
        return 2
 
    def add_plan(self, content: str) -> int:
        """Save a plan. Returns points earned."""
        plans = self._get_list('plans')
        plans.append({'id': len(plans) + 1, 'content': content,
                      'date': datetime.now().strftime('%Y-%m-%d'), 'completed': False})
        self._set_list('plans', plans)
        self._add_points(5, stat='mind')
        self.save()
        return 5
 
    def complete_plan(self, plan_id: int) -> int:
        """Mark a plan as completed. Returns points earned."""
        plans = self._get_list('plans')
        plan  = next((p for p in plans if p['id'] == plan_id), None)
 
        if not plan or plan.get('completed'):
            raise ValueError('Plan not found or already completed.')
 
        plan['completed']      = True
        plan['completed_date'] = datetime.now().strftime('%Y-%m-%d')
        self._set_list('plans', plans)
        self._add_points(3, stat='mind')
        self.save()
        return 3
 
 
class BudgetService(InventoryService):
    """Manages the budget tracker."""
 
    def add_transaction(self, t_type: str, amount: float,
                        category: str, description: str, date: str) -> float:
        """Add a transaction and return the new balance."""
        budget       = self._get_dict('budget')
        transactions = list(budget.get('transactions', []))
        transactions.append({
            'id':          len(transactions) + 1,
            'type':        t_type,
            'amount':      amount,
            'category':    category,
            'description': description,
            'date':        date,
        })
        budget['transactions'] = transactions[-100:]
        budget['balance']      = budget.get('balance', 0) + (amount if t_type == 'income' else -amount)
        self._set_dict('budget', budget)
        self._add_points(2, stat='mind')
        self.save()
        return budget['balance']
 
    def build_summary(self) -> dict:
        budget       = self._get_dict('budget')
        transactions = budget.get('transactions', [])
        month_prefix = datetime.now().strftime('%Y-%m')
 
        monthly_income   = sum(t['amount'] for t in transactions
                               if t['type'] == 'income' and t.get('date', '').startswith(month_prefix))
        monthly_expenses = sum(t['amount'] for t in transactions
                               if t['type'] == 'expense' and t.get('date', '').startswith(month_prefix))
        return {
            'monthly_income':      monthly_income,
            'monthly_expenses':    monthly_expenses,
            'recent_transactions': transactions[-10:],
        }
 
 
class ProgrammingService(InventoryService):
    """Tracks coding sessions and language XP."""
 
    XP_RATES    = {'practice': 1.0, 'tutorial': 0.8, 'project': 1.5, 'problem_solving': 2.0}
    BASE_POINTS = {'practice': 10,  'tutorial': 8,   'project': 15,  'problem_solving': 20}
 
    @staticmethod
    def default_skills() -> dict:
        return {
            'languages': {
                'python': {
                    'name': 'Python', 'level': 1, 'xp': 0,
                    'xp_to_next': 100, 'total_sessions': 0, 'total_hours': 0,
                }
            },
            'session_history': [],
        }
 
    def log_session(self, language: str, task_type: str,
                    duration: int, description: str) -> dict:
        """Log a coding session. Returns xp_earned, points, and leveled_up."""
        prog      = self._get_dict('prog_skills') or self.default_skills()
        languages = dict(prog.get('languages', {}))
 
        if language not in languages:
            languages[language] = {
                'name': language.title(), 'level': 1, 'xp': 0,
                'xp_to_next': 100, 'total_sessions': 0, 'total_hours': 0,
            }
 
        lang      = dict(languages[language])
        xp_earned = int(duration * self.XP_RATES.get(task_type, 1.0))
        points    = self.BASE_POINTS.get(task_type, 10)
        if duration >= 60:  points += 5
        if duration >= 120: points += 10
 
        lang['xp']             += xp_earned
        lang['total_sessions']  = lang.get('total_sessions', 0) + 1
        lang['total_hours']     = round(lang.get('total_hours', 0) + duration / 60, 2)
 
        leveled_up = False
        while lang['xp'] >= lang['xp_to_next']:
            lang['xp']         -= lang['xp_to_next']
            lang['level']      += 1
            lang['xp_to_next']  = int(100 * (1.2 ** (lang['level'] - 1)))
            leveled_up = True
 
        languages[language] = lang
        history = list(prog.get('session_history', []))
        history.append({
            'language': language, 'date': datetime.now().strftime('%Y-%m-%d'),
            'duration_minutes': duration, 'task_type': task_type,
            'description': description, 'xp_earned': xp_earned,
        })
        prog['languages']       = languages
        prog['session_history'] = history[-50:]
        self._set_dict('prog_skills', prog)
        self._add_points(points, stat='mind')
        self.save()
 
        return {'xp_earned': xp_earned, 'points': points, 'leveled_up': leveled_up}
 
 
class NemesisService(InventoryService):
    """Controls Nemesis Mode — high-stakes daily accountability."""
 
    def activate(self, non_negotiables: list) -> None:
        if not non_negotiables:
            raise ValueError('Select at least 1 non-negotiable.')
        nemesis = self._get_dict('nemesis_mode')
        nemesis['active']          = True
        nemesis['non_negotiables'] = non_negotiables
        self._set_dict('nemesis_mode', nemesis)
        self.save()
 
    def deactivate(self) -> None:
        nemesis = self._get_dict('nemesis_mode')
        nemesis['active'] = False
        self._set_dict('nemesis_mode', nemesis)
        self.save()
 
    def check_and_penalise(self, streaks_completed: list) -> bool:
        """
        If Nemesis Mode is active and a non-negotiable was missed,
        increment the gauge and return True so the caller can zero the points.
        """
        nemesis = self._get_dict('nemesis_mode')
        if not nemesis.get('active'):
            return False
 
        for non_negotiable in nemesis.get('non_negotiables', []):
            if non_negotiable not in streaks_completed:
                nemesis['gauge'] = min(100, nemesis.get('gauge', 0) + 10)
                self._set_dict('nemesis_mode', nemesis)
                return True
 
        return False
 
 
class WorkoutService(InventoryService):
    """Manages workout templates and logged sessions."""
 
    def save_template(self, name: str, day: str, exercises_text: str) -> None:
        ws             = self._get_dict('workout_sessions')
        templates      = dict(ws.get('templates', {}))
        template_id    = name.lower().replace(' ', '_')
        exercise_list  = [e.strip() for e in exercises_text.splitlines() if e.strip()]
 
        templates[template_id] = {
            'id': template_id, 'name': name, 'day': day,
            'exercises': exercise_list,
            'created': datetime.now().strftime('%Y-%m-%d'),
        }
        ws['templates'] = templates
        self._set_dict('workout_sessions', ws)
        self.save()
 
    def delete_template(self, template_id: str) -> None:
        ws        = self._get_dict('workout_sessions')
        templates = dict(ws.get('templates', {}))
        templates.pop(template_id, None)
        ws['templates'] = templates
        self._set_dict('workout_sessions', ws)
        self.save()
 
    def log_session(self, template_id: str, completed_exercises: list,
                    duration: int, notes_text: str) -> int:
        """Log a completed workout session. Returns points earned."""
        ws        = self._get_dict('workout_sessions')
        history   = list(ws.get('history', []))
        templates = ws.get('templates', {})
        template  = templates.get(template_id, {})
 
        history.append({
            'id':                  len(history) + 1,
            'template_id':         template_id,
            'template_name':       template.get('name', 'Custom'),
            'date':                datetime.now().strftime('%Y-%m-%d'),
            'exercises_completed': completed_exercises,
            'duration_minutes':    duration,
            'notes':               notes_text,
        })
        points = 25 + min(len(completed_exercises) * 2, 15)
        ws['history'] = history[-50:]
        self._set_dict('workout_sessions', ws)
        self._add_points(points, stat='body')
        self.save()
        return points
 
 
class PersonalRecordService(InventoryService):
    """Tracks personal records for gym exercises."""
 
    def log(self, exercise: str, weight: float, reps: int, sets: int) -> dict:
        """
        Log a PR attempt. Returns a result dict with is_pr, points,
        improvement_percent, old_volume, and new_volume.
        """
        records    = self._get_dict('personal_records')
        exercises  = dict(records.get('exercises', {}))
        new_volume = weight * reps * sets
        result     = {'is_pr': False, 'points': 0, 'improvement_percent': 0,
                      'old_volume': 0, 'new_volume': new_volume}
 
        if exercise in exercises:
            old        = exercises[exercise]
            old_volume = old['weight'] * old['reps'] * old['sets']
            result['old_volume'] = old_volume
 
            if new_volume > old_volume:
                improvement = ((new_volume - old_volume) / old_volume * 100) if old_volume else 100
                points      = 8 if improvement >= 20 else 7 if improvement >= 10 else 6 if improvement >= 5 else 5
                exercises[exercise] = {
                    'weight': weight, 'reps': reps, 'sets': sets,
                    'volume': new_volume, 'date': datetime.now().strftime('%Y-%m-%d'),
                    'previous_volume': old_volume,
                }
                result.update({'is_pr': True, 'points': points,
                               'improvement_percent': round(improvement, 1)})
        else:
            exercises[exercise] = {
                'weight': weight, 'reps': reps, 'sets': sets,
                'volume': new_volume, 'date': datetime.now().strftime('%Y-%m-%d'),
                'previous_volume': 0,
            }
            result.update({'is_pr': True, 'points': 5})
 
        if result['is_pr']:
            records['exercises'] = exercises
            self._set_dict('personal_records', records)
            self._add_points(result['points'], stat='body')
            self.save()
 
        return result
 
    def delete(self, exercise: str) -> None:
        records   = self._get_dict('personal_records')
        exercises = dict(records.get('exercises', {}))
        exercises.pop(exercise, None)
        records['exercises'] = exercises
        self._set_dict('personal_records', records)
        self.save()
 
 
class OnboardingService(BaseService):
    """Handles the first-login onboarding flow."""
 
    def is_complete(self) -> bool:
        return bool((self.character.skill_tree or {}).get('onboarded'))
 
    def complete(self, focus: str, intensity: str, obstacle: str) -> None:
        """Award starter XP and store answers; marks character as onboarded."""
        xp_grant = ONBOARD_FOCUS_XP.get(focus, ONBOARD_FOCUS_XP['all'])
        self.character.stats = update_stats(self.character.stats or {}, xp_grant)
 
        skill_tree = dict(self.character.skill_tree or {})
        skill_tree.update({
            'onboarded':         True,
            'onboard_focus':     focus,
            'onboard_intensity': intensity,
            'onboard_obstacle':  obstacle,
            'priority_tasks':    ONBOARD_PRIORITY_TASKS.get(focus, []),
            'highlight_streak':  ONBOARD_OBSTACLE_STREAKS.get(obstacle, 'morning_routine'),
        })
        self.character.skill_tree = skill_tree
        flag_modified(self.character, 'stats')
        flag_modified(self.character, 'skill_tree')
        db.session.commit()
 
 
class ActivityLogService(BaseService):
    """
    Handles the full log-activity flow:
    parse form → calculate points → update streaks → check combos →
    apply nemesis penalty → update stats → return result for the route to persist.
    """
 
    def log(self, form, log_date_str: str) -> dict:
        tier2             = {a: (a in form) for a in TIER2_ACTIVITIES}
        tier3             = {a: (a in form) for a in TIER3_ACTIVITIES}
        tier1_complete    = 'tier1_complete' in form
        streaks_completed = [s for s in STREAK_NAMES if s in form]
 
        points  = calculate_tier1_points(tier1_complete)
        points += calculate_activity_points(tier2)
        stat_xp = calculate_stat_xp(tier2, tier3)
 
        self.character.streaks, streak_points, streak_xp = update_streaks(
            self.character.streaks or init_streaks(), streaks_completed, log_date_str
        )
        points += streak_points
        for stat, xp in streak_xp.items():
            stat_xp[stat] = stat_xp.get(stat, 0) + xp
 
        activities_done = [a for a, done in tier2.items() if done]
        combos          = check_combos(activities_done)
        combo_bonus     = calculate_combo_bonus(combos)
        points         += combo_bonus
 
        penalised = NemesisService(self.character).check_and_penalise(streaks_completed)
        if penalised:
            points = 0
 
        self.character.stats = update_stats(self.character.stats or {}, stat_xp)
        self._add_points(points)
 
        return {
            'points':            points,
            'combo_bonus':       combo_bonus,
            'combos':            combos,
            'tier1_complete':    tier1_complete,
            'tier2':             tier2,
            'tier3':             tier3,
            'streaks_completed': streaks_completed,
            'penalised':         penalised,
        }
 
 
# ══════════════════════════════════════════════════════════════════════════════
# Dashboard builder — assembles all template context for the index view
# ══════════════════════════════════════════════════════════════════════════════
 
class DashboardBuilder:
    """
    Collects and assembles all data required to render index.html.
    Call build() to get a dict ready to unpack into render_template.
    """
 
    def __init__(self, character: Character, user_id: int):
        self.character = character
        self.user_id   = user_id
 
    def build(self) -> dict:
        return {
            'character':              self.character,
            'stats':                  self._build_stats(),
            'active_streaks':         self._build_active_streaks(),
            'logs':                   CharacterRepository.get_logs(self.user_id, limit=10),
            'now':                    datetime.now(),
            'challenge_data':         ChallengeService(self.character).get_today(),
            'analytics':              self._build_analytics(),
            'skill_tree_locked':      SkillTreeService(self.character).get_locked(),
            'skill_tree_unlocked':    SkillTreeService(self.character).get_unlocked(),
            'achievements_earned':    self.character.achievements or [],
            'achievements_available': self._build_available_achievements(),
            'notes':                  (self.character.notes or [])[-20:],
            'plans':                  [p for p in (self.character.plans or []) if not p.get('completed')],
            'nemesis':                self.character.nemesis_mode or {'active': False, 'non_negotiables': [], 'gauge': 0},
            'budget':                 self.character.budget or {'balance': 0, 'transactions': []},
            'budget_summary':         BudgetService(self.character).build_summary(),
            'prog_skills':            self.character.prog_skills or ProgrammingService.default_skills(),
            'personal_records':       self.character.personal_records or {'exercises': {}},
            'workout_sessions':       self.character.workout_sessions or {'templates': {}, 'history': []},
            'ghost_data':             self._build_ghost_data(),
        }
 
    def _build_stats(self) -> dict:
        stats = {}
        for stat_name in ('body', 'mind', 'soul'):
            data       = self.character.stats.get(stat_name, DEFAULT_STATS[stat_name])
            xp         = data.get('xp', 0)
            xp_to_next = data.get('xp_to_next', 100)
            level      = data.get('level', 1)
            progress   = max(0, min(int((xp / xp_to_next) * 100) if xp_to_next else 0, 100))
            stats[stat_name] = {'level': level, 'xp': xp, 'xp_to_next': xp_to_next, 'progress': progress}
        return stats
 
    def _build_active_streaks(self) -> dict:
        return {
            k: v for k, v in (self.character.streaks or {}).items()
            if isinstance(v, dict) and v.get('current', 0) > 0
        }
 
    def _build_available_achievements(self) -> list:
        earned_ids = [a['id'] for a in (self.character.achievements or [])]
        return [a for a in ACHIEVEMENTS_LIST if a['id'] not in earned_ids]
 
    def _build_analytics(self) -> dict:
        logs = CharacterRepository.get_logs(self.user_id, limit=30, order='asc')
        if not logs:
            return {'total_days': 0, 'average_points': 0, 'best_day': 0,
                    'worst_day': 0, 'weekly_trend': [], 'top_activities': []}
 
        points_list = [log.total_points for log in logs]
        breakdown   = {}
        for log in logs:
            for activity, done in (log.tier2 or {}).items():
                if done:
                    breakdown[activity] = breakdown.get(activity, 0) + 1
 
        top_activities = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:8]
        weekly, chunk  = [], []
        for log in reversed(logs):
            chunk.append(log.total_points)
            if len(chunk) == 7:
                weekly.insert(0, {'points': sum(chunk), 'avg': round(sum(chunk) / 7, 1)})
                chunk = []
 
        return {
            'total_days':     len(logs),
            'average_points': round(sum(points_list) / len(points_list), 1),
            'best_day':       max(points_list),
            'worst_day':      min(points_list),
            'weekly_trend':   weekly[-4:],
            'top_activities': top_activities,
        }
 
    def _build_ghost_data(self) -> dict:
        logs = CharacterRepository.get_logs(self.user_id, order='asc')
        if len(logs) < 7:
            return {'has_ghost': False, 'message': 'Need at least 7 days of data'}
 
        recent_week = logs[-7:]
        weekly_avg  = round(sum(log.total_points for log in recent_week) / 7, 1)
        best_week   = max(
            sum(log.total_points for log in logs[i:i+7])
            for i in range(len(logs) - 6)
        ) if len(logs) >= 14 else 0
 
        today_str       = datetime.now().strftime('%Y-%m-%d')
        last_week_str   = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        today_entry     = next((l for l in logs if l.date.strftime('%Y-%m-%d') == today_str), None)
        last_week_entry = next((l for l in logs if l.date.strftime('%Y-%m-%d') == last_week_str), None)
        today_pts       = today_entry.total_points if today_entry else 0
        last_week_pts   = last_week_entry.total_points if last_week_entry else 0
 
        return {
            'has_ghost':      True,
            'weekly_average': weekly_avg,
            'best_week':      best_week,
            'today':          today_pts,
            'last_week':      last_week_pts,
            'difference':     today_pts - last_week_pts,
            'winning':        today_pts >= last_week_pts,
            'total_days':     len(logs),
        }
 
 
# ══════════════════════════════════════════════════════════════════════════════
# Routes — thin wrappers; no business logic here
# ══════════════════════════════════════════════════════════════════════════════
 
def _redirect_home():
    return redirect(url_for('main.index'))
 
 
@bp.route('/edit-username', methods=['POST'])
@login_required
def edit_username():
    new_username  = request.form.get('username')
    existing_user = User.query.filter_by(username=new_username).first()
 
    if current_user.username == new_username:
        flash('New username matches the old one', 'error')
    elif existing_user and existing_user.id != current_user.id:
        flash('Username already taken', 'error')
    else:
        current_user.username = new_username
        db.session.commit()
        flash('Username updated!', 'success')
 
    return _redirect_home()
 
 
@bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    character = CharacterRepository.get_or_create(current_user.id)
    service   = OnboardingService(character)
 
    if service.is_complete():
        return _redirect_home()
 
    if request.method == 'POST':
        service.complete(
            focus     = request.form.get('focus', 'all'),
            intensity = request.form.get('intensity', 'moderate'),
            obstacle  = request.form.get('obstacle', 'consistency'),
        )
        flash(f'Welcome, {current_user.username}. Your warrior has been forged.', 'success')
        return _redirect_home()
 
    return render_template('onboarding.html')
 
 
@bp.route('/')
@login_required
def index():
    character = CharacterRepository.get_or_create(current_user.id)
 
    if not OnboardingService(character).is_complete():
        return redirect(url_for('main.onboarding'))
 
    context = DashboardBuilder(character, current_user.id).build()
    return render_template('index.html', **context)
 
 
@bp.route('/log-activity', methods=['POST'])
@login_required
def log_activity():
    try:
        log_date_str = request.form.get('log_date') or datetime.now().strftime('%Y-%m-%d')
        log_date     = datetime.strptime(log_date_str, '%Y-%m-%d').date()
 
        if log_date > datetime.now().date():
            flash('Cannot log future dates', 'error')
            return _redirect_home()
 
        character = CharacterRepository.get_or_create(current_user.id)
        result    = ActivityLogService(character).log(request.form, log_date_str)
 
        if result['penalised']:
            flash('😈 Nemesis Mode: non-negotiable broken — points zeroed.', 'error')
 
        existing_log = DailyLog.query.filter_by(user_id=current_user.id, date=log_date).first()
        if existing_log:
            existing_log.total_points += result['points']
            existing_log.tier2         = {**existing_log.tier2, **result['tier2']}
            existing_log.combos        = list(set((existing_log.combos or []) + [c['name'] for c in result['combos']]))
            existing_log.combo_bonus   = (existing_log.combo_bonus or 0) + result['combo_bonus']
            flag_modified(existing_log, 'tier2')
            flag_modified(existing_log, 'combos')
        else:
            db.session.add(DailyLog(
                user_id=current_user.id, date=log_date,
                total_points=result['points'], tier1_complete=result['tier1_complete'],
                tier2=result['tier2'], tier3=result['tier3'],
                combos=[c['name'] for c in result['combos']],
                combo_bonus=result['combo_bonus'],
                notes=request.form.get('notes', ''),
            ))
 
        recent_logs = CharacterRepository.get_logs(current_user.id, limit=7)
        AchievementService(character).check_all(recent_logs)
        CharacterRepository.save(character)
 
        flash(f"✅ Quest logged! +{result['points']} points", 'success')
        if result['combos']:
            combo_names = ', '.join(c['name'] for c in result['combos'])
            flash(f"⚡ Combos: {combo_names}! +{result['combo_bonus']} bonus", 'success')
 
    except Exception:
        traceback.print_exc()
        flash('Error logging activity', 'error')
 
    return _redirect_home()
 
 
@bp.route('/complete-challenge', methods=['POST'])
@login_required
def complete_challenge():
    try:
        character = CharacterRepository.get_or_create(current_user.id)
        points    = ChallengeService(character).complete()
        flash(f'🎯 Challenge complete! +{points}p', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception:
        traceback.print_exc()
        flash('Error completing challenge', 'error')
    return _redirect_home()
 
 
@bp.route('/unlock-skill', methods=['POST'])
@login_required
def unlock_skill():
    try:
        character = CharacterRepository.get_or_create(current_user.id)
        skill     = SkillTreeService(character).unlock(request.form.get('skill_id'))
        flash(f"🔓 Unlocked: {skill['name']}!", 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception:
        traceback.print_exc()
        flash('Error unlocking skill', 'error')
    return _redirect_home()
 
 
@bp.route('/add-note', methods=['POST'])
@login_required
def add_note():
    try:
        content   = request.form.get('content', '').strip()
        note_type = request.form.get('note_type', 'note')
 
        if not content:
            flash('Cannot save empty note', 'error')
            return _redirect_home()
 
        character = CharacterRepository.get_or_create(current_user.id)
        service   = NoteService(character)
 
        if note_type == 'plan':
            points = service.add_plan(content)
            flash(f'📋 Plan added! +{points}p', 'success')
        else:
            points = service.add_note(content)
            flash(f'📝 Note saved! +{points}p', 'success')
 
    except Exception:
        traceback.print_exc()
        flash('Error saving note', 'error')
    return _redirect_home()
 
 
@bp.route('/complete-plan/<int:plan_id>', methods=['POST'])
@login_required
def complete_plan(plan_id):
    try:
        character = CharacterRepository.get_or_create(current_user.id)
        points    = NoteService(character).complete_plan(plan_id)
        flash(f'✅ Plan completed! +{points}p', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception:
        traceback.print_exc()
        flash('Error completing plan', 'error')
    return _redirect_home()
 
 
@bp.route('/add-transaction', methods=['POST'])
@login_required
def add_transaction():
    try:
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Amount must be positive', 'error')
            return _redirect_home()
 
        character   = CharacterRepository.get_or_create(current_user.id)
        new_balance = BudgetService(character).add_transaction(
            t_type      = request.form.get('type'),
            amount      = amount,
            category    = request.form.get('category', 'Other'),
            description = request.form.get('description', ''),
            date        = request.form.get('date', datetime.now().strftime('%Y-%m-%d')),
        )
        flash(f'💰 Transaction added! New balance: {new_balance:.2f} +2p', 'success')
    except Exception:
        traceback.print_exc()
        flash('Error adding transaction', 'error')
    return _redirect_home()
 
 
@bp.route('/log-prog-session', methods=['POST'])
@login_required
def log_prog_session():
    try:
        character = CharacterRepository.get_or_create(current_user.id)
        result    = ProgrammingService(character).log_session(
            language    = request.form.get('language', 'python'),
            task_type   = request.form.get('task_type', 'practice'),
            duration    = int(request.form.get('duration_minutes', 30)),
            description = request.form.get('description', ''),
        )
        level_up_text = ' 🆙 LEVEL UP!' if result['leveled_up'] else ''
        flash(f"💻 Session logged! +{result['points']}p{level_up_text}", 'success')
    except Exception:
        traceback.print_exc()
        flash('Error logging session', 'error')
    return _redirect_home()
 
 
@bp.route('/toggle-nemesis', methods=['POST'])
@login_required
def toggle_nemesis():
    try:
        character = CharacterRepository.get_or_create(current_user.id)
        service   = NemesisService(character)
 
        if request.form.get('action') == 'activate':
            service.activate(request.form.getlist('non_negotiables'))
            flash('😈 Nemesis Mode ACTIVATED. No excuses.', 'success')
        else:
            service.deactivate()
            flash('Nemesis Mode deactivated', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception:
        traceback.print_exc()
        flash('Error toggling nemesis mode', 'error')
    return _redirect_home()
 
 
@bp.route('/log-personal-record', methods=['POST'])
@login_required
def log_personal_record():
    try:
        exercise = request.form.get('exercise_name', '').strip()
        if not exercise:
            flash('Exercise name required', 'error')
            return _redirect_home()
 
        character = CharacterRepository.get_or_create(current_user.id)
        result    = PersonalRecordService(character).log(
            exercise = exercise,
            weight   = float(request.form.get('weight', 0)),
            reps     = int(request.form.get('reps', 0)),
            sets     = int(request.form.get('sets', 1)),
        )
        if result['is_pr']:
            flash(f"🏆 New PR on {exercise}! +{result['points']}p", 'success')
        else:
            flash(f"Logged {exercise} — not a PR yet (best: {result['old_volume']:.0f} vol)", 'success')
 
    except Exception:
        traceback.print_exc()
        flash('Error logging personal record', 'error')
    return _redirect_home()
 
 
@bp.route('/delete-personal-record', methods=['POST'])
@login_required
def delete_personal_record():
    try:
        exercise  = request.form.get('exercise_name', '').strip()
        character = CharacterRepository.get_or_create(current_user.id)
        PersonalRecordService(character).delete(exercise)
        flash(f'Deleted PR for {exercise}', 'success')
    except Exception:
        traceback.print_exc()
        flash('Error deleting record', 'error')
    return _redirect_home()
 
 
@bp.route('/save-workout-template', methods=['POST'])
@login_required
def save_workout_template():
    try:
        name = request.form.get('template_name', '').strip()
        if not name:
            flash('Template name required', 'error')
            return _redirect_home()
 
        character = CharacterRepository.get_or_create(current_user.id)
        WorkoutService(character).save_template(
            name           = name,
            day            = request.form.get('template_day', ''),
            exercises_text = request.form.get('template_exercises', ''),
        )
        flash(f'✅ Template "{name}" saved!', 'success')
    except Exception:
        traceback.print_exc()
        flash('Error saving template', 'error')
    return _redirect_home()
 
 
@bp.route('/delete-workout-template', methods=['POST'])
@login_required
def delete_workout_template():
    try:
        character = CharacterRepository.get_or_create(current_user.id)
        WorkoutService(character).delete_template(request.form.get('template_id', ''))
        flash('Template deleted', 'success')
    except Exception:
        traceback.print_exc()
        flash('Error deleting template', 'error')
    return _redirect_home()
 
 
@bp.route('/log-workout-session', methods=['POST'])
@login_required
def log_workout_session():
    try:
        character = CharacterRepository.get_or_create(current_user.id)
        points    = WorkoutService(character).log_session(
            template_id         = request.form.get('template_id', ''),
            completed_exercises = request.form.getlist('completed_exercises'),
            duration            = int(request.form.get('duration_minutes', 0)),
            notes_text          = request.form.get('session_notes', ''),
        )
        flash(f'💪 Workout logged! +{points}p', 'success')
    except Exception:
        traceback.print_exc()
        flash('Error logging workout session', 'error')
    return _redirect_home()
 
 
@bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('auth.login'))

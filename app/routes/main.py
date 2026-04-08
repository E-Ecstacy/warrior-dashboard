"""Main Routes - All Features, Server-Side Rendering"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from copy import deepcopy
from sqlalchemy.orm.attributes import flag_modified
from app.models import User, db, Character, DailyLog
from app.features.points import calculate_activity_points, calculate_tier1_points
from app.features.stats import calculate_stat_xp, update_stats
from app.features.streaks import update_streaks
from app.features.combos import check_combos, calculate_combo_bonus
from app.features.leveling import calculate_level_up
from app.features.character_init import init_streaks, init_character_data

bp = Blueprint('main', __name__)

DEFAULT_STATS = {
    'body': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
    'mind': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
    'soul': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
}

SKILL_TREE_ITEMS = [
    {"id": "advanced_workout",   "name": "Advanced Workout Program",    "cost": 500,  "category": "body"},
    {"id": "premium_learning",   "name": "Premium Learning Platform",   "cost": 500,  "category": "mind"},
    {"id": "coding_course",      "name": "Advanced Programming Course", "cost": 500,  "category": "mind"},
    {"id": "project_equipment",  "name": "New Dev Equipment/Tools",     "cost": 500,  "category": "soul"},
    {"id": "cheat_day",          "name": "Guilt-Free Rest Day",         "cost": 500,  "category": "body"},
    {"id": "weekend_trip",       "name": "Weekend Experience/Trip",     "cost": 1000, "category": "body"},
    {"id": "mentor_session_rew", "name": "Mentor/Coach Session",        "cost": 1000, "category": "soul"},
    {"id": "dream_purchase",     "name": "Major Dream Purchase",        "cost": 2500, "category": "soul"},
    {"id": "certification",      "name": "Professional Certification",  "cost": 2500, "category": "mind"},
]

DAILY_CHALLENGES = [
    {"id": "no_caffeine",        "name": "No Caffeine Today",          "description": "No coffee, tea, or energy drinks",   "points": 15, "category": "body"},
    {"id": "read_1h",            "name": "Read for 1 Hour Straight",   "description": "No breaks, full focus reading",       "points": 20, "category": "mind"},
    {"id": "ice_bath",           "name": "10-Minute Cold Shower",      "description": "Cold exposure challenge",             "points": 30, "category": "body"},
    {"id": "teach_someone",      "name": "Teach Someone Something",    "description": "Share knowledge with another person", "points": 25, "category": "soul"},
    {"id": "no_social_media",    "name": "Zero Social Media",          "description": "Not even a peek",                    "points": 20, "category": "mind"},
    {"id": "wake_5am",           "name": "Wake Up at 5 AM",            "description": "Early bird special",                 "points": 15, "category": "mind"},
    {"id": "100_burpees",        "name": "100 Burpees",                "description": "All at once or throughout day",       "points": 25, "category": "body"},
    {"id": "no_screens_evening", "name": "No Screens After 8 PM",      "description": "Evening digital detox",              "points": 15, "category": "body"},
    {"id": "help_stranger",      "name": "Help a Stranger",            "description": "Random act of kindness",             "points": 20, "category": "soul"},
    {"id": "30min_meditation",   "name": "30-Minute Meditation",       "description": "Extended mindfulness session",        "points": 25, "category": "body"},
    {"id": "no_sugar",           "name": "No Sugar Today",             "description": "Zero added sugars",                  "points": 15, "category": "body"},
    {"id": "learn_new_concept",  "name": "Learn Something New",        "description": "Outside your comfort zone",          "points": 20, "category": "mind"},
    {"id": "write_1000_words",   "name": "Write 1000 Words",           "description": "Journal, blog, or creative writing", "points": 20, "category": "mind"},
    {"id": "no_complaints",      "name": "Don't Complain All Day",     "description": "Catch yourself, stay positive",      "points": 15, "category": "mind"},
    {"id": "silent_workout",     "name": "No Music During Workout",    "description": "Pure focus, no audio",               "points": 10, "category": "mind"},
]

ACHIEVEMENTS_LIST = [
    {"id": "week_warrior",  "name": "Week Warrior",      "description": "7 days of 100+ points",               "points_bonus": 50},
    {"id": "balanced_life", "name": "Balanced Life",     "description": "Hit all 3 stat categories in a week", "points_bonus": 50},
    {"id": "comeback_kid",  "name": "Comeback Kid",      "description": "200+ points after a <50p day",        "points_bonus": 30},
    {"id": "flow_state",    "name": "Flow State Master", "description": "4+ hours deep work in one day",       "points_bonus": 80},
    {"id": "digital_monk",  "name": "Digital Monk",      "description": "Zero screens entire day",             "points_bonus": 100},
    {"id": "streak_legend", "name": "Streak Legend",     "description": "30-day streak on any activity",       "points_bonus": 100},
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

@bp.route('/edit-username', methods=['POST'])
@login_required
def edit_username():
    new_username = request.form.get('username')
    existing_user = User.query.filter_by(username=new_username).first()
    if current_user.username == new_username:
        flash("New usernames matches with the old one" , "error")
    elif existing_user and existing_user.id != current_user.id:
        flash("Username already taken", "error")
    else:
        flash("Username updated!", 'success')
        current_user.username = new_username
        db.session.commit()
        return redirect(url_for('main.index'))

def get_or_create_character():
    character = Character.query.filter_by(user_id=current_user.id).first()
    if not character:
        character = Character(
            user_id=current_user.id,
            stats=init_character_data()['stats'],
            streaks=init_streaks()
        )
        db.session.add(character)
        db.session.commit()
    if not character.stats or not isinstance(character.stats, dict):
        character.stats = init_character_data()['stats']
        db.session.commit()
    return character


def build_stats_with_progress(character):
    stats = {}
    for stat_name in ['body', 'mind', 'soul']:
        d = character.stats.get(stat_name, DEFAULT_STATS[stat_name])
        xp, xp_to_next, level = d.get('xp', 0), d.get('xp_to_next', 100), d.get('level', 1)
        progress = max(0, min(int((xp / xp_to_next) * 100) if xp_to_next else 0, 100))
        stats[stat_name] = {'level': level, 'xp': xp, 'xp_to_next': xp_to_next, 'progress': progress}
    return stats


def get_today_challenge(character):
    import random
    challenge_data = character.daily_challenge or {}
    today = datetime.now().strftime('%Y-%m-%d')
    if challenge_data.get('date') != today:
        challenge_data = {
            'date': today,
            'challenge': random.choice(DAILY_CHALLENGES),
            'completed': False
        }
        character.daily_challenge = deepcopy(challenge_data)
        flag_modified(character, 'daily_challenge')
        db.session.commit()
    return challenge_data


def check_and_award_achievements(character, logs):
    earned_ids = [a['id'] for a in (character.achievements or [])]
    pts = [l.total_points for l in logs]

    if 'week_warrior' not in earned_ids and len(pts) >= 7:
        if all(p >= 100 for p in pts[:7]):
            _grant_achievement(character, 'week_warrior')

    if 'streak_legend' not in earned_ids:
        for s in (character.streaks or {}).values():
            if isinstance(s, dict) and s.get('current', 0) >= 30:
                _grant_achievement(character, 'streak_legend')
                break


def _grant_achievement(character, achievement_id):
    match = next((a for a in ACHIEVEMENTS_LIST if a['id'] == achievement_id), None)
    if not match:
        return None
    earned = list(character.achievements or [])
    earned.append({**match, 'date_earned': datetime.now().strftime('%Y-%m-%d')})
    character.achievements = earned
    flag_modified(character, 'achievements')
    character.total_points += match['points_bonus']
    flash(f'🏆 Achievement: {match["name"]}! +{match["points_bonus"]}p', 'success')
    return match


def save_character(character):
    """Force SQLAlchemy to detect all JSON mutations."""
    for col in ['stats', 'streaks', 'achievements', 'skill_tree',
                'daily_challenge', 'notes', 'plans',
                'nemesis_mode', 'budget', 'prog_skills']:
        val = getattr(character, col, None)
        if val is not None:
            setattr(character, col, deepcopy(val))
            flag_modified(character, col)
    db.session.commit()


def _build_analytics(logs):
    if not logs:
        return {'total_days': 0, 'average_points': 0, 'best_day': 0,
                'worst_day': 0, 'weekly_trend': [], 'top_activities': []}
    pts = [l.total_points for l in logs]
    breakdown = {}
    for log in logs:
        for activity, done in (log.tier2 or {}).items():
            if done:
                breakdown[activity] = breakdown.get(activity, 0) + 1
    top_activities = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:8]
    weekly, chunk = [], []
    for log in reversed(logs):
        chunk.append(log.total_points)
        if len(chunk) == 7:
            weekly.insert(0, {'points': sum(chunk), 'avg': round(sum(chunk) / 7, 1)})
            chunk = []
    return {
        'total_days': len(logs),
        'average_points': round(sum(pts) / len(pts), 1),
        'best_day': max(pts),
        'worst_day': min(pts),
        'weekly_trend': weekly[-4:],
        'top_activities': top_activities,
    }


def _build_budget_summary(budget):
    transactions = (budget or {}).get('transactions', [])
    current_month = datetime.now().strftime('%Y-%m')
    monthly_income   = sum(t['amount'] for t in transactions if t['type'] == 'income'  and t.get('date', '').startswith(current_month))
    monthly_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense' and t.get('date', '').startswith(current_month))
    return {'monthly_income': monthly_income, 'monthly_expenses': monthly_expenses,
            'recent_transactions': transactions[-10:]}


def _default_prog_skills():
    return {'languages': {'python': {'name': 'Python', 'level': 1, 'xp': 0,
            'xp_to_next': 100, 'total_sessions': 0, 'total_hours': 0}},
            'session_history': []}


def _build_ghost_data(logs):
    if len(logs) < 7:
        return {'has_ghost': False, 'message': 'Need at least 7 days of data'}

    recent_week = logs[-7:]
    weekly_avg  = round(sum(l.total_points for l in recent_week) / 7, 1)

    best_week = 0
    if len(logs) >= 14:
        for i in range(len(logs) - 6):
            week_pts = sum(l.total_points for l in logs[i:i+7])
            if week_pts > best_week:
                best_week = week_pts

    today_str      = datetime.now().strftime('%Y-%m-%d')
    last_week_str  = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    from datetime import date as date_type
    today_entry     = next((l for l in logs if l.date.strftime('%Y-%m-%d') == today_str), None)
    last_week_entry = next((l for l in logs if l.date.strftime('%Y-%m-%d') == last_week_str), None)
    today_pts       = today_entry.total_points if today_entry else 0
    last_week_pts   = last_week_entry.total_points if last_week_entry else 0

    return {
        'has_ghost': True,
        'weekly_average': weekly_avg,
        'best_week': best_week,
        'today': today_pts,
        'last_week': last_week_pts,
        'difference': today_pts - last_week_pts,
        'winning': today_pts >= last_week_pts,
        'total_days': len(logs),
    }


# ─── Routes ───────────────────────────────────────────────────────────────────

@bp.route('/')
@login_required
def index():
    character = get_or_create_character()
    stats = build_stats_with_progress(character)

    active_streaks = {
        k: v for k, v in (character.streaks or {}).items()
        if isinstance(v, dict) and v.get('current', 0) > 0
    }

    logs = DailyLog.query.filter_by(user_id=current_user.id)\
        .order_by(DailyLog.date.desc()).limit(10).all()

    challenge_data = get_today_challenge(character)

    all_logs = DailyLog.query.filter_by(user_id=current_user.id)\
        .order_by(DailyLog.date.asc()).limit(30).all()
    analytics = _build_analytics(all_logs)

    # Skill tree
    skill_tree    = character.skill_tree or {}
    unlocked_ids  = [s['id'] for s in skill_tree.get('unlocked', [])]
    skill_tree_locked    = [s for s in SKILL_TREE_ITEMS if s['id'] not in unlocked_ids]
    skill_tree_unlocked  = skill_tree.get('unlocked', [])

    # Achievements
    earned_ids             = [a['id'] for a in (character.achievements or [])]
    achievements_earned    = character.achievements or []
    achievements_available = [a for a in ACHIEVEMENTS_LIST if a['id'] not in earned_ids]

    # Notes & Plans
    notes        = (character.notes or [])[-20:]
    active_plans = [p for p in (character.plans or []) if not p.get('completed')]

    # Nemesis
    nemesis = character.nemesis_mode or {'active': False, 'non_negotiables': [], 'gauge': 0}

    # Budget
    budget         = character.budget or {'balance': 0, 'transactions': []}
    budget_summary = _build_budget_summary(budget)

    # Coding / Prog skills
    prog_skills = character.prog_skills or _default_prog_skills()

    # Personal Records
    personal_records = character.personal_records or {'exercises': {}}

    # Workout Sessions
    workout_sessions = character.workout_sessions or {'templates': {}, 'history': []}

    # Ghost Data — compare this week vs last week
    all_logs_ghost = DailyLog.query.filter_by(user_id=current_user.id)\
        .order_by(DailyLog.date.asc()).all()
    ghost_data = _build_ghost_data(all_logs_ghost)

    return render_template('index.html',
        character=character,
        stats=stats,
        active_streaks=active_streaks,
        logs=logs,
        now=datetime.now(),
        challenge_data=challenge_data,
        analytics=analytics,
        skill_tree_locked=skill_tree_locked,
        skill_tree_unlocked=skill_tree_unlocked,
        achievements_earned=achievements_earned,
        achievements_available=achievements_available,
        notes=notes,
        plans=active_plans,
        nemesis=nemesis,
        budget=budget,
        budget_summary=budget_summary,
        prog_skills=prog_skills,
        personal_records=personal_records,
        workout_sessions=workout_sessions,
        ghost_data=ghost_data,
    )


@bp.route('/log-activity', methods=['POST'])
@login_required
def log_activity():
    try:
        log_date_str = request.form.get('log_date') or datetime.now().strftime('%Y-%m-%d')
        log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
        if log_date > datetime.now().date():
            flash('Cannot log future dates', 'error')
            return redirect(url_for('main.index'))

        character = get_or_create_character()
        tier1_complete = 'tier1_complete' in request.form

        tier2_activities = [
            'full_workout','light_exercise','stretching','cold_shower',
            'deep_work','read_book','code_practice','meditation',
            'push_ups_100','steps_10k','study_pomodoro','project_dev',
            'part_time_job','new_skill','kinnu','online_course','journal',
            'screen_under_2h','screen_2_4h','no_phone_morning','no_phone_night',
            'plan_tomorrow','organize_space','budget_review',
            'gratitude','breathwork','nature_walk',
            'code_project','write_docs','build_design','open_source',
            'meaningful_conversation','help_someone_code','call_family',
            'help_someone','teach_someone','give_advice','active_listening',
            'encourage_someone','group_activity','networking',
            'compliment_someone','thank_someone','check_in','quality_time',
        ]
        tier2 = {a: (a in request.form) for a in tier2_activities}

        tier3_activities = ['flow_state_4h', 'zero_screens', 'complete_todo',
                            'cold_exposure', 'new_algorithm', 'teach_code']
        tier3 = {a: (a in request.form) for a in tier3_activities}

        streak_names = ['no_porn','workout','meditation','deep_work','reading',
                        'coding_practice','sleep_7h','morning_routine',
                        'no_doomscroll','screen_time_under_2h']
        streaks_completed = [s for s in streak_names if s in request.form]

        points = calculate_tier1_points(tier1_complete)
        points += calculate_activity_points(tier2)
        stat_xp = calculate_stat_xp(tier2, tier3)

        character.streaks, streak_points, streak_xp = update_streaks(
            character.streaks or init_streaks(), streaks_completed, log_date_str)
        points += streak_points
        for sn, xp in streak_xp.items():
            stat_xp[sn] = stat_xp.get(sn, 0) + xp

        activities_done = [a for a, done in tier2.items() if done]
        combos      = check_combos(activities_done)
        combo_bonus = calculate_combo_bonus(combos)
        points     += combo_bonus

        # Nemesis check — zero points if non-negotiable broken
        nemesis = character.nemesis_mode or {}
        if nemesis.get('active'):
            for nn in nemesis.get('non_negotiables', []):
                if nn not in streaks_completed:
                    points = 0
                    nemesis['gauge'] = min(100, nemesis.get('gauge', 0) + 10)
                    character.nemesis_mode = deepcopy(nemesis)
                    flag_modified(character, 'nemesis_mode')
                    flash('😈 Nemesis Mode: non-negotiable broken! Points zeroed.', 'error')
                    break

        character.stats = update_stats(character.stats or {}, stat_xp)
        character.total_points += points
        character.current_week_points += points
        character.level = calculate_level_up(character.total_points)

        existing_log = DailyLog.query.filter_by(user_id=current_user.id, date=log_date).first()
        if existing_log:
            existing_log.total_points += points
            existing_log.tier2 = {**existing_log.tier2, **tier2}
            existing_log.combos = list(set((existing_log.combos or []) + [c['name'] for c in combos]))
            existing_log.combo_bonus = (existing_log.combo_bonus or 0) + combo_bonus
            flag_modified(existing_log, 'tier2')
            flag_modified(existing_log, 'combos')
        else:
            db.session.add(DailyLog(
                user_id=current_user.id, date=log_date,
                total_points=points, tier1_complete=tier1_complete,
                tier2=tier2, tier3=tier3,
                combos=[c['name'] for c in combos],
                combo_bonus=combo_bonus,
                notes=request.form.get('notes', '')
            ))

        # Check achievements
        recent_logs = DailyLog.query.filter_by(user_id=current_user.id)\
            .order_by(DailyLog.date.desc()).limit(7).all()
        check_and_award_achievements(character, recent_logs)

        save_character(character)

        flash(f'✅ Quest logged! +{points} points', 'success')
        if combos:
            flash(f'⚡ Combos: {", ".join(c["name"] for c in combos)}! +{combo_bonus} bonus', 'success')

        return redirect(url_for('main.index'))
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error logging activity', 'error')
        return redirect(url_for('main.index'))


@bp.route('/complete-challenge', methods=['POST'])
@login_required
def complete_challenge():
    try:
        character = get_or_create_character()
        challenge_data = character.daily_challenge or {}
        today = datetime.now().strftime('%Y-%m-%d')
        if challenge_data.get('date') != today:
            flash('No challenge for today', 'error')
            return redirect(url_for('main.index'))
        if challenge_data.get('completed'):
            flash('Already completed today!', 'error')
            return redirect(url_for('main.index'))
        challenge = challenge_data['challenge']
        points = challenge['points']
        challenge_data['completed'] = True
        character.daily_challenge = deepcopy(challenge_data)
        character.total_points += points
        character.current_week_points += points
        character.stats = update_stats(character.stats or {}, {challenge.get('category', 'mind'): points})
        save_character(character)
        flash(f'🎯 Challenge complete! +{points}p', 'success')
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error completing challenge', 'error')
    return redirect(url_for('main.index'))


@bp.route('/unlock-skill', methods=['POST'])
@login_required
def unlock_skill():
    try:
        skill_id  = request.form.get('skill_id')
        character = get_or_create_character()
        skill     = next((s for s in SKILL_TREE_ITEMS if s['id'] == skill_id), None)
        if not skill:
            flash('Skill not found', 'error')
            return redirect(url_for('main.index'))
        if character.total_points < skill['cost']:
            flash(f'Need {skill["cost"]}p — you have {character.total_points}p', 'error')
            return redirect(url_for('main.index'))
        tree     = character.skill_tree or {'unlocked': []}
        unlocked = tree.get('unlocked', [])
        if any(s['id'] == skill_id for s in unlocked):
            flash('Already unlocked!', 'error')
            return redirect(url_for('main.index'))
        character.total_points -= skill['cost']
        unlocked.append({**skill, 'date_unlocked': datetime.now().strftime('%Y-%m-%d')})
        tree['unlocked'] = unlocked
        character.skill_tree = deepcopy(tree)
        save_character(character)
        flash(f'🔓 Unlocked: {skill["name"]}!', 'success')
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error unlocking skill', 'error')
    return redirect(url_for('main.index'))


@bp.route('/add-note', methods=['POST'])
@login_required
def add_note():
    try:
        character = get_or_create_character()
        note_type = request.form.get('note_type', 'note')
        content   = request.form.get('content', '').strip()
        if not content:
            flash('Cannot save empty note', 'error')
            return redirect(url_for('main.index'))
        today = datetime.now().strftime('%Y-%m-%d')
        if note_type == 'plan':
            plans = list(character.plans or [])
            plans.append({'id': len(plans) + 1, 'content': content, 'date': today, 'completed': False})
            character.plans = plans
            character.total_points += 5
            character.stats = update_stats(character.stats or {}, {'mind': 5})
            flash('📋 Plan added! +5p', 'success')
        else:
            notes = list(character.notes or [])
            notes.append({'id': len(notes) + 1, 'content': content, 'date': today})
            character.notes = notes[-50:]
            character.total_points += 2
            character.stats = update_stats(character.stats or {}, {'mind': 2})
            flash('📝 Note saved! +2p', 'success')
        save_character(character)
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error saving note', 'error')
    return redirect(url_for('main.index'))


@bp.route('/complete-plan/<int:plan_id>', methods=['POST'])
@login_required
def complete_plan(plan_id):
    try:
        character = get_or_create_character()
        plans     = list(character.plans or [])
        plan      = next((p for p in plans if p['id'] == plan_id), None)
        if plan and not plan.get('completed'):
            plan['completed'] = True
            plan['completed_date'] = datetime.now().strftime('%Y-%m-%d')
            character.plans = plans
            character.total_points += 3
            character.stats = update_stats(character.stats or {}, {'mind': 3})
            save_character(character)
            flash('✅ Plan completed! +3p', 'success')
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error completing plan', 'error')
    return redirect(url_for('main.index'))


@bp.route('/add-transaction', methods=['POST'])
@login_required
def add_transaction():
    try:
        character = get_or_create_character()
        budget    = dict(character.budget or {'balance': 0, 'transactions': []})
        t_type    = request.form.get('type')
        amount    = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Amount must be positive', 'error')
            return redirect(url_for('main.index'))
        transactions = list(budget.get('transactions', []))
        transactions.append({
            'id': len(transactions) + 1,
            'type': t_type,
            'amount': amount,
            'category': request.form.get('category', 'Other'),
            'description': request.form.get('description', ''),
            'date': request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        })
        budget['transactions'] = transactions[-100:]
        budget['balance'] = budget.get('balance', 0) + (amount if t_type == 'income' else -amount)
        character.budget = budget
        character.total_points += 2
        character.stats = update_stats(character.stats or {}, {'mind': 2})
        save_character(character)
        flash('💰 Transaction added! +2p', 'success')
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error adding transaction', 'error')
    return redirect(url_for('main.index'))


@bp.route('/log-prog-session', methods=['POST'])
@login_required
def log_prog_session():
    try:
        character   = get_or_create_character()
        prog        = dict(character.prog_skills or _default_prog_skills())
        language    = request.form.get('language', 'python')
        duration    = int(request.form.get('duration_minutes', 30))
        task_type   = request.form.get('task_type', 'practice')
        description = request.form.get('description', '')

        languages = dict(prog.get('languages', {}))
        if language not in languages:
            languages[language] = {'name': language.title(), 'level': 1, 'xp': 0,
                                   'xp_to_next': 100, 'total_sessions': 0, 'total_hours': 0}

        lang = dict(languages[language])
        xp_rates  = {'practice': 1, 'tutorial': 0.8, 'project': 1.5, 'problem_solving': 2}
        pts_base  = {'practice': 10, 'tutorial': 8,  'project': 15,  'problem_solving': 20}
        xp_earned     = int(duration * xp_rates.get(task_type, 1))
        points_earned = pts_base.get(task_type, 10)
        if duration >= 60:  points_earned += 5
        if duration >= 120: points_earned += 10

        lang['xp']             += xp_earned
        lang['total_sessions']  = lang.get('total_sessions', 0) + 1
        lang['total_hours']     = round(lang.get('total_hours', 0) + duration / 60, 2)

        leveled_up = False
        while lang['xp'] >= lang['xp_to_next']:
            lang['xp']       -= lang['xp_to_next']
            lang['level']    += 1
            lang['xp_to_next'] = int(100 * (1.2 ** (lang['level'] - 1)))
            leveled_up = True

        languages[language] = lang
        history = list(prog.get('session_history', []))
        history.append({'language': language, 'date': datetime.now().strftime('%Y-%m-%d'),
                        'duration_minutes': duration, 'task_type': task_type,
                        'description': description, 'xp_earned': xp_earned})
        prog['languages']       = languages
        prog['session_history'] = history[-50:]
        character.prog_skills   = prog
        character.total_points += points_earned
        character.stats = update_stats(character.stats or {}, {'mind': points_earned})
        save_character(character)
        flash(f'💻 Session logged! +{points_earned}p' + (' 🆙 LEVEL UP!' if leveled_up else ''), 'success')
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error logging session', 'error')
    return redirect(url_for('main.index'))


@bp.route('/toggle-nemesis', methods=['POST'])
@login_required
def toggle_nemesis():
    try:
        character = get_or_create_character()
        nemesis   = dict(character.nemesis_mode or {'active': False, 'non_negotiables': [], 'gauge': 0})
        action    = request.form.get('action')
        if action == 'activate':
            non_neg = request.form.getlist('non_negotiables')
            if not non_neg:
                flash('Select at least 1 non-negotiable', 'error')
                return redirect(url_for('main.index'))
            nemesis['active']           = True
            nemesis['non_negotiables']  = non_neg
            flash('😈 Nemesis Mode ACTIVATED. No excuses.', 'success')
        else:
            nemesis['active'] = False
            flash('Nemesis Mode deactivated', 'success')
        character.nemesis_mode = nemesis
        save_character(character)
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error toggling nemesis mode', 'error')
    return redirect(url_for('main.index'))


@bp.route('/log-personal-record', methods=['POST'])
@login_required
def log_personal_record():
    try:
        character    = get_or_create_character()
        records      = dict(character.personal_records or {})
        exercises    = dict(records.get('exercises', {}))
        exercise     = request.form.get('exercise_name', '').strip()
        weight       = float(request.form.get('weight', 0))
        reps         = int(request.form.get('reps', 0))
        sets         = int(request.form.get('sets', 1))

        if not exercise:
            flash('Exercise name required', 'error')
            return redirect(url_for('main.index'))

        new_volume = weight * reps * sets
        is_pr      = False
        points     = 0
        old_volume = 0

        if exercise in exercises:
            old = exercises[exercise]
            old_volume = old['weight'] * old['reps'] * old['sets']
            if new_volume > old_volume:
                is_pr = True
                pct   = ((new_volume - old_volume) / old_volume) * 100 if old_volume else 100
                points = 8 if pct >= 20 else 7 if pct >= 10 else 6 if pct >= 5 else 5
                exercises[exercise] = {
                    'weight': weight, 'reps': reps, 'sets': sets,
                    'volume': new_volume, 'date': datetime.now().strftime('%Y-%m-%d'),
                    'previous_volume': old_volume
                }
                flash(f'🏆 NEW PR on {exercise}! +{points}p', 'success')
            else:
                flash(f'Logged {exercise} — not a PR yet (best: {old_volume:.0f} vol)', 'success')
        else:
            is_pr  = True
            points = 5
            exercises[exercise] = {
                'weight': weight, 'reps': reps, 'sets': sets,
                'volume': new_volume, 'date': datetime.now().strftime('%Y-%m-%d'),
                'previous_volume': 0
            }
            flash(f'🏆 First PR logged for {exercise}! +{points}p', 'success')

        if is_pr and points:
            character.total_points += points
            character.stats = update_stats(character.stats or {}, {'body': points})

        records['exercises'] = exercises
        character.personal_records = records
        save_character(character)

    except Exception:
        import traceback; traceback.print_exc()
        flash('Error logging personal record', 'error')
    return redirect(url_for('main.index'))


@bp.route('/delete-personal-record', methods=['POST'])
@login_required
def delete_personal_record():
    try:
        character = get_or_create_character()
        records   = dict(character.personal_records or {})
        exercises = dict(records.get('exercises', {}))
        exercise  = request.form.get('exercise_name', '').strip()
        if exercise in exercises:
            del exercises[exercise]
            records['exercises'] = exercises
            character.personal_records = records
            save_character(character)
            flash(f'Deleted PR for {exercise}', 'success')
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error deleting record', 'error')
    return redirect(url_for('main.index'))


@bp.route('/save-workout-template', methods=['POST'])
@login_required
def save_workout_template():
    try:
        character = get_or_create_character()
        ws        = dict(character.workout_sessions or {'templates': {}, 'history': []})
        templates = dict(ws.get('templates', {}))

        name      = request.form.get('template_name', '').strip()
        day       = request.form.get('template_day', '')
        exercises = request.form.get('template_exercises', '')  # newline-separated

        if not name:
            flash('Template name required', 'error')
            return redirect(url_for('main.index'))

        template_id = name.lower().replace(' ', '_')
        exercise_list = [e.strip() for e in exercises.splitlines() if e.strip()]

        templates[template_id] = {
            'id': template_id, 'name': name, 'day': day,
            'exercises': exercise_list,
            'created': datetime.now().strftime('%Y-%m-%d')
        }
        ws['templates'] = templates
        character.workout_sessions = ws
        save_character(character)
        flash(f'✅ Template "{name}" saved!', 'success')
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error saving template', 'error')
    return redirect(url_for('main.index'))


@bp.route('/delete-workout-template', methods=['POST'])
@login_required
def delete_workout_template():
    try:
        character   = get_or_create_character()
        ws          = dict(character.workout_sessions or {'templates': {}, 'history': []})
        template_id = request.form.get('template_id', '')
        templates   = dict(ws.get('templates', {}))
        if template_id in templates:
            del templates[template_id]
            ws['templates'] = templates
            character.workout_sessions = ws
            save_character(character)
            flash('Template deleted', 'success')
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error deleting template', 'error')
    return redirect(url_for('main.index'))


@bp.route('/log-workout-session', methods=['POST'])
@login_required
def log_workout_session():
    try:
        character   = get_or_create_character()
        ws          = dict(character.workout_sessions or {'templates': {}, 'history': []})
        history     = list(ws.get('history', []))
        template_id = request.form.get('template_id', '')
        templates   = ws.get('templates', {})
        template    = templates.get(template_id, {})
        duration    = int(request.form.get('duration_minutes', 0))
        notes_text  = request.form.get('session_notes', '')

        # Which exercises were completed (checkboxes)
        completed_exercises = request.form.getlist('completed_exercises')

        session = {
            'id': len(history) + 1,
            'template_id': template_id,
            'template_name': template.get('name', 'Custom'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'exercises_completed': completed_exercises,
            'duration_minutes': duration,
            'notes': notes_text
        }
        history.append(session)

        # Points: base 25 + up to 15 bonus for exercises
        points = 25 + min(len(completed_exercises) * 2, 15)
        character.total_points  += points
        character.stats = update_stats(character.stats or {}, {'body': points})

        ws['history'] = history[-50:]
        character.workout_sessions = ws
        save_character(character)
        flash(f'💪 Workout logged! +{points}p', 'success')
    except Exception:
        import traceback; traceback.print_exc()
        flash('Error logging workout session', 'error')
    return redirect(url_for('main.index'))


@bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('auth.login'))

"""Main Routes - Bulletproof with Defaults"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Character, DailyLog
from app.features.points import calculate_activity_points, calculate_tier1_points
from app.features.stats import calculate_stat_xp, update_stats
from app.features.streaks import update_streaks
from app.features.combos import check_combos, calculate_combo_bonus
from app.features.leveling import calculate_level_up
from app.features.character_init import init_streaks, init_character_data

bp = Blueprint('main', __name__)

# Default stats - guaranteed to work
DEFAULT_STATS = {
    'strength': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
    'intellect': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
    'discipline': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
    'energy': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
    'influence': {'level': 1, 'xp': 0, 'xp_to_next': 100, 'progress': 0},
}

@bp.route('/')
@login_required
def index():
    """Main dashboard - bulletproof"""
    character = Character.query.filter_by(user_id=current_user.id).first()
    
    if not character:
        character = Character(
            user_id=current_user.id,
            stats=init_character_data()['stats'],
            streaks=init_streaks()
        )
        db.session.add(character)
        db.session.commit()
    
    # Safety: fix broken stats
    if not character.stats or not isinstance(character.stats, dict):
        character.stats = init_character_data()['stats']
        db.session.commit()
    
    # Calculate progress with fallbacks
    stats_with_progress = {}
    for stat_name in ['strength', 'intellect', 'discipline', 'energy', 'influence']:
        stat_data = character.stats.get(stat_name, DEFAULT_STATS[stat_name])
        
        xp = stat_data.get('xp', 0)
        xp_to_next = stat_data.get('xp_to_next', 100)
        level = stat_data.get('level', 1)
        
        if xp_to_next > 0:
            progress = int((xp / xp_to_next) * 100)
        else:
            progress = 0
        
        progress = max(0, min(progress, 100))
        
        stats_with_progress[stat_name] = {
            'level': level,
            'xp': xp,
            'xp_to_next': xp_to_next,
            'progress': progress
        }
    
    # Active streaks with safety
    active_streaks = {}
    if character.streaks and isinstance(character.streaks, dict):
        for streak_name, streak_data in character.streaks.items():
            if isinstance(streak_data, dict) and streak_data.get('current', 0) > 0:
                active_streaks[streak_name] = streak_data
    
    logs = DailyLog.query.filter_by(user_id=current_user.id)\
        .order_by(DailyLog.date.desc())\
        .limit(10)\
        .all()
    print("="*50)
    print(f"Character: {character}")
    print(f"Character.stats: {character.stats}")
    print(f"Stats with progress: {stats_with_progress}")
    print(f"Active streaks: {active_streaks}")
    print(f"Logs: {logs}")
    print("="*50)

    # GUARANTEED all variables exist
    return render_template('index.html',
                         character=character,
                         stats=stats_with_progress,
                         active_streaks=active_streaks,
                         logs=logs,
                         now=datetime.now())

@bp.route('/log-activity', methods=['POST'])
@login_required
def log_activity():
    """Process activity logging"""
    try:
        log_date_str = request.form.get('log_date') or datetime.now().strftime('%Y-%m-%d')
        log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
        
        if log_date > datetime.now().date():
            flash('Cannot log future dates', 'error')
            return redirect(url_for('main.index'))
        
        character = Character.query.filter_by(user_id=current_user.id).first()
        if not character:
            flash('Character not found', 'error')
            return redirect(url_for('main.index'))
        
        tier1_complete = 'tier1_complete' in request.form
        
        tier2 = {}
        tier2_activities = [
            'full_workout', 'light_exercise', 'stretching', 'cold_shower',
            'deep_work', 'read_book', 'code_practice', 'meditation'
        ]
        for activity in tier2_activities:
            tier2[activity] = activity in request.form
        
        tier3 = {}
        
        streaks_completed = []
        streak_names = ['no_porn', 'workout', 'meditation']
        for streak in streak_names:
            if streak in request.form:
                streaks_completed.append(streak)
        
        points = calculate_tier1_points(tier1_complete)
        points += calculate_activity_points(tier2)
        
        stat_xp = calculate_stat_xp(tier2, tier3)
        
        character.streaks, streak_points, streak_xp = update_streaks(
            character.streaks or init_streaks(), 
            streaks_completed, 
            log_date_str
        )
        points += streak_points
        
        for stat_name, xp in streak_xp.items():
            stat_xp[stat_name] = stat_xp.get(stat_name, 0) + xp
        
        activities_done = [a for a, done in tier2.items() if done]
        combos = check_combos(activities_done)
        combo_bonus = calculate_combo_bonus(combos)
        points += combo_bonus
        
        character.stats = update_stats(character.stats or {}, stat_xp)
        # CRITICAL: SQLAlchemy can't detect mutations inside JSON columns.
        # We must reassign to a new dict to force it to detect the change.
        from copy import deepcopy
        character.stats = deepcopy(character.stats)
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(character, 'stats')
        flag_modified(character, 'streaks')
        character.total_points += points
        character.current_week_points += points
        character.level = calculate_level_up(character.total_points)
        
        existing_log = DailyLog.query.filter_by(
            user_id=current_user.id, 
            date=log_date
        ).first()
        
        if existing_log:
            existing_log.total_points += points
            existing_log.tier2 = {**existing_log.tier2, **tier2}
            existing_log.combos = [c['name'] for c in combos]
            existing_log.combo_bonus += combo_bonus
        else:
            log = DailyLog(
                user_id=current_user.id,
                date=log_date,
                total_points=points,
                tier1_complete=tier1_complete,
                tier2=tier2,
                tier3=tier3,
                combos=[c['name'] for c in combos],
                combo_bonus=combo_bonus,
                notes=request.form.get('notes', '')
            )
            db.session.add(log)
        
        db.session.commit()
        
        flash(f'✅ Quest logged! +{points} points', 'success')
        if combos:
            combo_names = ', '.join([c['name'] for c in combos])
            flash(f'⚡ Combos: {combo_names}! +{combo_bonus} bonus', 'success')
        
        return redirect(url_for('main.index'))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error logging activity', 'error')
        return redirect(url_for('main.index'))

@bp.route('/logout')
def logout():
    """Logout"""
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('auth.login'))

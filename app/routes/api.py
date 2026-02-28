"""API Routes - Orchestrates All Features"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Character, DailyLog
from app.features.points import calculate_activity_points, calculate_tier1_points
from app.features.stats import calculate_stat_xp, update_stats
from app.features.streaks import update_streaks
from app.features.combos import check_combos, calculate_combo_bonus
from app.features.leveling import calculate_level_up
from app.features.analytics import calculate_analytics

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/character', methods=['GET'])
@login_required
def get_character():
    """Get character data"""
    character = Character.query.filter_by(user_id=current_user.id).first()
    
    if not character:
        return jsonify({'error': 'Character not found'}), 404
    
    return jsonify({
        'level': character.level,
        'total_points': character.total_points,
        'current_week_points': character.current_week_points,
        'stats': character.stats,
        'streaks': character.streaks
    })

@bp.route('/daily-log', methods=['GET', 'POST'])
@login_required
def daily_log():
    """Handle daily logs"""
    if request.method == 'GET':
        logs = DailyLog.query.filter_by(user_id=current_user.id)\
            .order_by(DailyLog.date.desc())\
            .limit(30)\
            .all()
        
        return jsonify([{
            'date': log.date.strftime('%Y-%m-%d'),
            'total_points': log.total_points,
            'tier1_complete': log.tier1_complete,
            'tier2': log.tier2,
            'tier3': log.tier3,
            'combos': log.combos,
            'combo_bonus': log.combo_bonus,
            'notes': log.notes
        } for log in logs])
    
    # POST - Create/update log
    data = request.json
    log_date_str = data.get('log_date') or datetime.now().strftime('%Y-%m-%d')
    log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
    
    # Validate not future
    if log_date > datetime.now().date():
        return jsonify({'error': 'Cannot log future dates'}), 400
    
    # Get character
    character = Character.query.filter_by(user_id=current_user.id).first()
    
    # Calculate points using features
    tier1_complete = data.get('tier1_complete', False)
    tier2 = data.get('tier2', {})
    tier3 = data.get('tier3', {})
    streaks_completed = data.get('streaks_completed', [])
    
    # 1. Activity points
    points = calculate_tier1_points(tier1_complete)
    points += calculate_activity_points(tier2)
    points += calculate_activity_points(tier3)
    
    # 2. Stat XP
    stat_xp = calculate_stat_xp(tier2, tier3)
    
    # 3. Streaks
    character.streaks, streak_points, streak_xp = update_streaks(
        character.streaks, streaks_completed, log_date_str
    )
    points += streak_points
    
    # Combine stat XP
    for stat_name, xp in streak_xp.items():
        stat_xp[stat_name] += xp
    
    # 4. Combos
    activities_done = [a for a, done in tier2.items() if done]
    combos = check_combos(activities_done)
    combo_bonus = calculate_combo_bonus(combos)
    points += combo_bonus
    
    # 5. Update character stats
    character.stats = update_stats(character.stats, stat_xp)
    character.total_points += points
    character.current_week_points += points
    character.level = calculate_level_up(character.total_points)
    
    # 6. Save or update log
    existing_log = DailyLog.query.filter_by(
        user_id=current_user.id, date=log_date
    ).first()
    
    if existing_log:
        existing_log.total_points += points
        existing_log.tier2 = {**existing_log.tier2, **tier2}
        existing_log.combos = combos
        existing_log.combo_bonus = combo_bonus
    else:
        log = DailyLog(
            user_id=current_user.id,
            date=log_date,
            total_points=points,
            tier1_complete=tier1_complete,
            tier2=tier2,
            tier3=tier3,
            combos=combos,
            combo_bonus=combo_bonus,
            notes=data.get('notes', '')
        )
        db.session.add(log)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'total_points': points,
        'combos': combos,
        'combo_bonus': combo_bonus
    })

@bp.route('/analytics', methods=['GET'])
@login_required
def get_analytics():
    """Get analytics data"""
    logs = DailyLog.query.filter_by(user_id=current_user.id)\
        .order_by(DailyLog.date)\
        .all()
    
    logs_data = [{
        'date': log.date.strftime('%Y-%m-%d'),
        'total_points': log.total_points,
        'tier2': log.tier2
    } for log in logs]
    
    analytics = calculate_analytics(logs_data)
    
    return jsonify(analytics)

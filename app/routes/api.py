"""API Routes - Complete Implementation with Proper Error Handling"""
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
from app.features.character_init import init_streaks, init_character_data

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/character', methods=['GET'])
@login_required
def get_character():
    """Get character data"""
    try:
        character = Character.query.filter_by(user_id=current_user.id).first()
        
        if not character:
            # Create character if doesn't exist
            character = Character(
                user_id=current_user.id,
                stats=init_character_data()['stats'],
                streaks=init_streaks()
            )
            db.session.add(character)
            db.session.commit()
        
        return jsonify({
            'character': {
                'level': character.level,
                'total_points': character.total_points,
                'current_week_points': character.current_week_points,
                'stats': character.stats or {}
            }
        })
    except Exception as e:
        print(f"Error in /api/character: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/streaks', methods=['GET'])
@login_required
def get_streaks():
    """Get streak data"""
    try:
        character = Character.query.filter_by(user_id=current_user.id).first()
        
        if not character:
            return jsonify({'streaks': init_streaks()})
        
        return jsonify({'streaks': character.streaks or init_streaks()})
    except Exception as e:
        print(f"Error in /api/streaks: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/achievements', methods=['GET'])
@login_required
def get_achievements():
    """Get achievements"""
    return jsonify({
        'earned': [],
        'available': []
    })

@bp.route('/daily-log', methods=['GET', 'POST'])
@login_required
def daily_log():
    """Handle daily logs"""
    if request.method == 'GET':
        try:
            logs = DailyLog.query.filter_by(user_id=current_user.id)\
                .order_by(DailyLog.date.desc())\
                .limit(30)\
                .all()
            
            return jsonify([{
                'date': log.date.strftime('%Y-%m-%d'),
                'total_points': log.total_points,
                'tier1_complete': log.tier1_complete,
                'tier2': log.tier2 or {},
                'tier3': log.tier3 or {},
                'combos_activated': log.combos or [],
                'combo_bonus': log.combo_bonus,
                'notes': log.notes,
                'energy_score': log.energy_score
            } for log in logs])
        except Exception as e:
            print(f"Error in GET /api/daily-log: {e}")
            return jsonify({'error': str(e)}), 500
    
    # POST
    try:
        data = request.json
        log_date_str = data.get('log_date') or datetime.now().strftime('%Y-%m-%d')
        log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
        
        if log_date > datetime.now().date():
            return jsonify({'success': False, 'error': 'Cannot log future dates'}), 400
        
        character = Character.query.filter_by(user_id=current_user.id).first()
        
        if not character:
            character = Character(
                user_id=current_user.id,
                stats=init_character_data()['stats'],
                streaks=init_streaks()
            )
            db.session.add(character)
            db.session.commit()
        
        # Calculate points
        tier1_complete = data.get('tier1_complete', False)
        tier2 = data.get('tier2', {})
        tier3 = data.get('tier3', {})
        streaks_completed = data.get('streaks_completed', [])
        
        points = calculate_tier1_points(tier1_complete)
        points += calculate_activity_points(tier2)
        points += calculate_activity_points(tier3)
        
        stat_xp = calculate_stat_xp(tier2, tier3)
        
        character.streaks, streak_points, streak_xp = update_streaks(
            character.streaks or init_streaks(), streaks_completed, log_date_str
        )
        points += streak_points
        
        for stat_name, xp in streak_xp.items():
            stat_xp[stat_name] = stat_xp.get(stat_name, 0) + xp
        
        activities_done = [a for a, done in tier2.items() if done]
        combos = check_combos(activities_done)
        combo_bonus = calculate_combo_bonus(combos)
        points += combo_bonus
        
        character.stats = update_stats(character.stats or {}, stat_xp)
        character.total_points += points
        character.current_week_points += points
        character.level = calculate_level_up(character.total_points)
        
        existing_log = DailyLog.query.filter_by(
            user_id=current_user.id, date=log_date
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
                notes=data.get('notes', ''),
                energy_score=data.get('energy_score')
            )
            db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'total_points': points,
            'combos_activated': [c['name'] for c in combos],
            'combo_bonus': combo_bonus
        })
    except Exception as e:
        print(f"Error in POST /api/daily-log: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/analytics', methods=['GET'])
@login_required
def get_analytics():
    """Get analytics data"""
    try:
        logs = DailyLog.query.filter_by(user_id=current_user.id)\
            .order_by(DailyLog.date)\
            .all()
        
        logs_data = [{
            'date': log.date.strftime('%Y-%m-%d'),
            'total_points': log.total_points,
            'tier2': log.tier2 or {}
        } for log in logs]
        
        analytics = calculate_analytics(logs_data)
        return jsonify(analytics)
    except Exception as e:
        print(f"Error in /api/analytics: {e}")
        return jsonify({'error': str(e)}), 500

# Placeholder endpoints
@bp.route('/skill-tree/unlock/<skill_id>', methods=['POST'])
@login_required
def unlock_skill(skill_id):
    return jsonify({'success': False, 'message': 'Feature coming soon'})

@bp.route('/personal-records', methods=['GET', 'POST', 'DELETE'])
@login_required
def personal_records():
    if request.method == 'GET':
        return jsonify([])
    return jsonify({'success': False, 'message': 'Feature coming soon'})

@bp.route('/notes', methods=['GET', 'POST', 'DELETE'])
@login_required
def notes():
    if request.method == 'GET':
        return jsonify([])
    return jsonify({'success': False, 'message': 'Feature coming soon'})

@bp.route('/notes/complete-plan/<plan_id>', methods=['POST'])
@login_required
def complete_plan(plan_id):
    return jsonify({'success': False, 'message': 'Feature coming soon'})

@bp.route('/daily-challenge', methods=['GET'])
@login_required
def daily_challenge():
    return jsonify({
        'id': 1,
        'title': 'Daily Challenge',
        'description': 'Complete your daily activities',
        'points_reward': 50,
        'completed': False
    })

@bp.route('/daily-challenge/complete', methods=['POST'])
@login_required
def complete_challenge():
    return jsonify({'success': False, 'message': 'Feature coming soon'})

@bp.route('/nemesis-mode', methods=['GET'])
@login_required
def nemesis_mode():
    return jsonify({
        'active': False,
        'non_negotiables': [],
        'nemesis_gauge': 0
    })

@bp.route('/ghost-data', methods=['GET'])
@login_required
def ghost_data():
    return jsonify({
        'today': 0,
        'last_week_today': 0,
        'best_week': 0
    })

@bp.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    if request.method == 'GET':
        return jsonify([])
    return jsonify({'success': False, 'message': 'Feature coming soon'})

@bp.route('/workout', methods=['GET', 'POST'])
@login_required
def workout():
    if request.method == 'GET':
        return jsonify([])
    return jsonify({'success': False, 'message': 'Feature coming soon'})

@bp.route('/programming-skills', methods=['GET', 'POST'])
@login_required
def programming_skills():
    if request.method == 'GET':
        return jsonify({
            'languages': {},
            'session_history': []
        })
    return jsonify({'success': False, 'message': 'Feature coming soon'})



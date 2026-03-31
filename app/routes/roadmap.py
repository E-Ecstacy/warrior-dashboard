"""Roadmap Blueprint — Warrior Roadmap feature."""
from datetime import date, timedelta
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
 
from app import db
from app.models import Character, DailyLog, RoadmapEntry
from app.features.stats import update_stats
from app.features.leveling import calculate_level_up
from app.constants.traits import TRAITS, LAYER_NAMES, CATEGORY_STAT_MAP, streak_multiplier
 
bp = Blueprint('roadmap', __name__, url_prefix='/roadmap')
 
 
# ── Helpers ───────────────────────────────────────────────────────────────────
 
def _get_or_create_entry(user_id: int, slug: str) -> RoadmapEntry:
    entry = RoadmapEntry.query.filter_by(user_id=user_id, trait_slug=slug).first()
    if not entry:
        entry = RoadmapEntry(user_id=user_id, trait_slug=slug)
        db.session.add(entry)
        try:
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            entry = RoadmapEntry.query.filter_by(user_id=user_id, trait_slug=slug).first()
    return entry
 
 
def _get_today_log() -> DailyLog | None:
    return DailyLog.query.filter_by(
        user_id=current_user.id, date=date.today()
    ).first()
 
 
def _activity_done_today(log, activity_slug) -> bool:
    if not log or not activity_slug:
        return False
    return bool((log.tier2 or {}).get(activity_slug, False))
 
 
def _get_or_create_character() -> Character:
    character = Character.query.filter_by(user_id=current_user.id).first()
    if not character:
        character = Character(user_id=current_user.id)
        db.session.add(character)
        db.session.flush()
    return character
 
 
def _award_points(character: Character, xp: int, stat_key: str):
    character.total_points = (character.total_points or 0) + xp
    character.current_week_points = (character.current_week_points or 0) + xp
    character.stats = update_stats(character.stats or {}, {stat_key: xp})
    character.level = calculate_level_up(character.total_points)
 
 
def _reverse_points(character: Character, xp: int, stat_key: str):
    character.total_points = max(0, (character.total_points or 0) - xp)
    character.current_week_points = max(0, (character.current_week_points or 0) - xp)
    stats = character.stats or {}
    stat = stats.get(stat_key, {})
    stat['xp'] = max(0, stat.get('xp', 0) - xp)
    character.stats = stats
    character.level = calculate_level_up(character.total_points)
 
 
# ── Routes ────────────────────────────────────────────────────────────────────
 
@bp.route('/')
@login_required
def index():
    today_log = _get_today_log()
 
    entries = {e.trait_slug: e for e in
               RoadmapEntry.query.filter_by(user_id=current_user.id).all()}
    for trait in TRAITS:
        if trait['slug'] not in entries:
            entries[trait['slug']] = _get_or_create_entry(current_user.id, trait['slug'])
    db.session.commit()
 
    rows = []
    for trait in TRAITS:
        slug = trait['slug']
        entry = entries[slug]
        already_counted = _activity_done_today(today_log, trait['dashboard_activity_slug'])
        rows.append({
            **trait,
            'streak':            entry.streak,
            'total_completions': entry.total_completions,
            'checked_today':     entry.checked_today(),
            'already_counted':   already_counted,
        })
 
    layers = []
    for layer_id, layer_name in LAYER_NAMES.items():
        layers.append({
            'id':     layer_id,
            'name':   layer_name,
            'traits': [r for r in rows if r['layer'] == layer_id],
        })
 
    today_xp = sum(e.last_xp_awarded for e in entries.values() if e.checked_today())
 
    category_counts = {}
    category_totals = {}
    for trait in TRAITS:
        cat = trait['category']
        category_totals[cat] = category_totals.get(cat, 0) + 1
        if entries[trait['slug']].checked_today():
            category_counts[cat] = category_counts.get(cat, 0) + 1
 
    return render_template(
        'roadmap/index.html',
        layers=layers,
        today_xp=today_xp,
        category_counts=category_counts,
        category_totals=category_totals,
        today=date.today().strftime('%A, %d %B %Y'),
    )
 
 
@bp.route('/check/<trait_slug>', methods=['POST'])
@login_required
def check_trait(trait_slug):
    trait = next((t for t in TRAITS if t['slug'] == trait_slug), None)
    if not trait:
        return jsonify(error='Unknown trait'), 404
 
    entry = _get_or_create_entry(current_user.id, trait_slug)
 
    # Idempotent guard
    if entry.checked_today():
        return jsonify(
            checked=True,
            xp_awarded=0,
            points_awarded=0,
            streak=entry.streak,
            already_counted=False,
        )
 
    today = date.today()
    yesterday = today - timedelta(days=1)
 
    # Streak logic
    if entry.last_completed_date is None or entry.last_completed_date < yesterday:
        entry.streak = 1
    elif entry.last_completed_date == yesterday:
        entry.streak += 1
    # if last_completed_date == today it means unchecked today — streak unchanged
 
    entry.last_completed_date = today
    entry.is_checked_today = True
    entry.total_completions += 1
 
    today_log = _get_today_log()
    already_counted = _activity_done_today(today_log, trait['dashboard_activity_slug'])
 
    xp_awarded = 0
    points_awarded = 0
 
    # Only award XP if never awarded today (last_xp_awarded is 0 after an uncheck)
    if not already_counted and entry.last_xp_awarded == 0:
        mult = streak_multiplier(entry.streak)
        xp_awarded     = round(trait['xp_reward'] * mult)
        points_awarded = round(trait['points_reward'] * mult)
        stat_key = CATEGORY_STAT_MAP[trait['category']]
        character = _get_or_create_character()
        _award_points(character, xp_awarded, stat_key)
 
    entry.last_xp_awarded     = xp_awarded
    entry.last_points_awarded = points_awarded
    db.session.commit()
 
    return jsonify(
        checked=True,
        xp_awarded=xp_awarded,
        points_awarded=points_awarded,
        streak=entry.streak,
        already_counted=already_counted,
    )
 
 
@bp.route('/uncheck/<trait_slug>', methods=['POST'])
@login_required
def uncheck_trait(trait_slug):
    trait = next((t for t in TRAITS if t['slug'] == trait_slug), None)
    if not trait:
        return jsonify(error='Unknown trait'), 404
 
    entry = RoadmapEntry.query.filter_by(
        user_id=current_user.id, trait_slug=trait_slug
    ).first()
 
    if not entry or not entry.checked_today():
        return jsonify(checked=False)
 
    if entry.last_xp_awarded > 0:
        stat_key = CATEGORY_STAT_MAP[trait['category']]
        character = _get_or_create_character()
        _reverse_points(character, entry.last_xp_awarded, stat_key)
 
    # Keep last_completed_date = today so streak logic knows we were here
    # Only flip the checked flag and zero awarded amounts
    entry.is_checked_today    = False
    entry.total_completions   = max(0, entry.total_completions - 1)
    entry.last_xp_awarded     = 0
    entry.last_points_awarded = 0
    db.session.commit()
 
    return jsonify(checked=False)

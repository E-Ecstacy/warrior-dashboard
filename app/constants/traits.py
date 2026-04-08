"""Warrior Roadmap — 24 trait definitions."""
from __future__ import annotations
 
 
class TraitRegistry:
    """
    Central registry for roadmap traits.
 
    Trait categories (used in TRAITS list):
        body    → maps to the 'body' stat
        mind    → maps to the 'mind' stat
        wealth  → maps to the 'mind' stat  (financial discipline = mental skill)
        social  → maps to the 'soul' stat
    """
 
    # Maps roadmap category → character.stats key (used with update_stats())
    CATEGORY_STAT_MAP: dict[str, str] = {
        'body':   'body',
        'mind':   'mind',
        'wealth': 'mind',
        'social': 'soul',
    }
 
    LAYER_NAMES: dict[int, str] = {
        0: 'Foundation',
        1: 'Identity',
        2: 'Skills',
        3: 'Body',
        4: 'Wealth',
    }
 
    @classmethod
    def stat_for(cls, category: str) -> str:
        """Return the character stat key for a given trait category."""
        return cls.CATEGORY_STAT_MAP.get(category, 'mind')
 
    @classmethod
    def by_layer(cls, layer: int) -> list[dict]:
        return [t for t in TRAITS if t['layer'] == layer]
 
    @classmethod
    def by_category(cls, category: str) -> list[dict]:
        return [t for t in TRAITS if t['category'] == category]
 
    @classmethod
    def by_slug(cls, slug: str) -> dict | None:
        return next((t for t in TRAITS if t['slug'] == slug), None)
 
    @staticmethod
    def streak_multiplier(streak: int) -> float:
        if streak >= 30: return 2.0
        if streak >= 14: return 1.5
        if streak >= 7:  return 1.25
        return 1.0
 
 
# dashboard_activity_slug maps to keys in DailyLog.tier2
TRAITS = [
    # ── Layer 0: Foundation ──────────────────────────────────────────
    {'slug': 'discipline_daily',           'name': 'Daily Discipline',            'layer': 0, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'morning_routine',            'name': 'Morning Routine',             'layer': 0, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': 'morning_routine'},
    {'slug': 'deep_work_session',          'name': 'Deep Work Session',           'layer': 0, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': 'deep_work'},
    {'slug': 'track_finances',             'name': 'Track Finances',              'layer': 0, 'category': 'wealth', 'xp_reward': 7, 'points_reward': 5, 'dashboard_activity_slug': 'budget_review'},
    {'slug': 'no_excuses',                 'name': 'No Excuses',                  'layer': 0, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'full_responsibility',        'name': 'Full Responsibility',         'layer': 0, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
 
    # ── Layer 1: Identity ────────────────────────────────────────────
    {'slug': 'strong_identity',            'name': 'Strong Identity',             'layer': 1, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'clear_life_vision',          'name': 'Clear Life Vision',           'layer': 1, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'emotional_control',          'name': 'Emotional Control',           'layer': 1, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'cut_toxic_relationships',    'name': 'Cut Toxic Relationships',     'layer': 1, 'category': 'social', 'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'self_reflection',            'name': 'Self Reflection',             'layer': 1, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': 'journal'},
 
    # ── Layer 2: Skills ──────────────────────────────────────────────
    {'slug': 'sales_skills',               'name': 'Sales Skills',                'layer': 2, 'category': 'social', 'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'communication',              'name': 'Communication',               'layer': 2, 'category': 'social', 'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'public_speaking',            'name': 'Public Speaking',             'layer': 2, 'category': 'social', 'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'intentional_networking',     'name': 'Intentional Networking',      'layer': 2, 'category': 'social', 'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': 'networking'},
    {'slug': 'master_focus',               'name': 'Master Focus',                'layer': 2, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
 
    # ── Layer 3: Body ────────────────────────────────────────────────
    {'slug': 'gym_training',               'name': 'Gym Training',                'layer': 3, 'category': 'body',   'xp_reward': 8, 'points_reward': 5, 'dashboard_activity_slug': 'full_workout'},
    {'slug': 'reduced_sugar',              'name': 'Reduced Sugar',               'layer': 3, 'category': 'body',   'xp_reward': 8, 'points_reward': 5, 'dashboard_activity_slug': None},
    {'slug': 'face_fears',                 'name': 'Face Your Fears',             'layer': 3, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'nofap_delay_gratification',  'name': 'NoFap / Delay Gratification', 'layer': 3, 'category': 'body',   'xp_reward': 8, 'points_reward': 5, 'dashboard_activity_slug': None},
 
    # ── Layer 4: Wealth ──────────────────────────────────────────────
    {'slug': 'invest_money',               'name': 'Invest Money',                'layer': 4, 'category': 'wealth', 'xp_reward': 7, 'points_reward': 5, 'dashboard_activity_slug': None},
    {'slug': 'multiple_income_streams',    'name': 'Multiple Income Streams',     'layer': 4, 'category': 'wealth', 'xp_reward': 7, 'points_reward': 5, 'dashboard_activity_slug': None},
    {'slug': 'obsessive_self_improvement', 'name': 'Obsessive Self-Improvement',  'layer': 4, 'category': 'mind',   'xp_reward': 6, 'points_reward': 4, 'dashboard_activity_slug': None},
    {'slug': 'delaying_gratification',     'name': 'Delaying Gratification',      'layer': 4, 'category': 'wealth', 'xp_reward': 7, 'points_reward': 5, 'dashboard_activity_slug': None},
]
 
# ── Module-level aliases (keeps existing call sites working) ───────────────────
LAYER_NAMES = TraitRegistry.LAYER_NAMES
CATEGORY_STAT_MAP = TraitRegistry.CATEGORY_STAT_MAP
streak_multiplier = TraitRegistry.streak_multiplier

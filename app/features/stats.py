"""Stat XP Distribution"""

def calculate_stat_xp(tier2, tier3):
    """Calculate XP for each stat based on activities"""
    stat_xp = {'strength': 0, 'intellect': 0, 'discipline': 0, 'energy': 0, 'influence': 0}
    
    # Physical (STRENGTH)
    if tier2.get('full_workout'): stat_xp['strength'] += 25
    if tier2.get('light_exercise'): stat_xp['strength'] += 12
    if tier2.get('push_ups_100'): stat_xp['strength'] += 20
    if tier2.get('steps_10k'): stat_xp['strength'] += 8
    if tier2.get('stretching'): stat_xp['strength'] += 5
    if tier2.get('cold_shower'): stat_xp['strength'] += 3
    
    # Mental (INTELLECT)
    if tier2.get('deep_work'): stat_xp['intellect'] += 20
    if tier2.get('study_pomodoro'): stat_xp['intellect'] += 15
    if tier2.get('project_dev'): stat_xp['intellect'] += 18
    if tier2.get('part_time_job'): stat_xp['intellect'] += 20
    if tier2.get('new_skill'): stat_xp['intellect'] += 12
    if tier2.get('read_book'): stat_xp['intellect'] += 10
    if tier2.get('kinnu'): stat_xp['intellect'] += 8
    if tier2.get('online_course'): stat_xp['intellect'] += 15
    if tier2.get('code_practice'): stat_xp['intellect'] += 15
    if tier2.get('code_project'): stat_xp['intellect'] += 25
    if tier2.get('new_algorithm'): stat_xp['intellect'] += 60
    
    # Digital Wellness (DISCIPLINE)
    if tier2.get('screen_under_2h'): stat_xp['discipline'] += 15
    if tier2.get('screen_2_4h'): stat_xp['discipline'] += 8
    if tier2.get('no_phone_morning'): stat_xp['discipline'] += 5
    if tier2.get('no_phone_night'): stat_xp['discipline'] += 5
    if tier2.get('plan_tomorrow'): stat_xp['discipline'] += 3
    if tier2.get('organize_space'): stat_xp['discipline'] += 5
    if tier2.get('budget_review'): stat_xp['discipline'] += 8
    if tier3.get('zero_screens'): stat_xp['discipline'] += 100
    if tier3.get('complete_todo'): stat_xp['discipline'] += 50
    
    # Mindfulness (ENERGY)
    if tier2.get('meditation'): stat_xp['energy'] += 8
    if tier2.get('gratitude'): stat_xp['energy'] += 3
    if tier2.get('breathwork'): stat_xp['energy'] += 5
    if tier2.get('nature_walk'): stat_xp['energy'] += 7
    if tier2.get('journal'): stat_xp['energy'] += 5
    if tier3.get('cold_exposure'): stat_xp['energy'] += 30
    
    # Social (INFLUENCE)
    if tier2.get('meaningful_conversation'): stat_xp['influence'] += 8
    if tier2.get('help_code'): stat_xp['influence'] += 10
    if tier2.get('call_family'): stat_xp['influence'] += 5
    if tier2.get('group_activity'): stat_xp['influence'] += 7
    if tier2.get('mentor_session'): stat_xp['influence'] += 8
    if tier2.get('networking'): stat_xp['influence'] += 6
    if tier2.get('compliment_someone'): stat_xp['influence'] += 2
    if tier2.get('thank_someone'): stat_xp['influence'] += 2
    if tier2.get('check_in'): stat_xp['influence'] += 3
    if tier2.get('quality_time'): stat_xp['influence'] += 10
    if tier3.get('teach_code'): stat_xp['influence'] += 40
    
    # Boss moves (INTELLECT)
    if tier3.get('flow_state_4h'): stat_xp['intellect'] += 80
    
    return stat_xp

def update_stats(stats, stat_xp):
    """Update character stats with earned XP - bulletproof version"""
    if not stats or not isinstance(stats, dict):
        stats = {}

    for stat_name, xp in stat_xp.items():
        if xp <= 0:
            continue  # Skip stats that earned nothing

        # Safe fallback if key is missing
        stat = stats.get(stat_name, {'level': 1, 'xp': 0, 'xp_to_next': 100})
        stats[stat_name] = stat  # Ensure it's written back

        stat['xp'] += xp

        # Level up if needed
        while stat['xp'] >= stat['xp_to_next']:
            stat['xp'] -= stat['xp_to_next']
            stat['level'] += 1
            stat['xp_to_next'] = int(100 * (1.2 ** (stat['level'] - 1)))

        print(f"  📊 {stat_name}: +{xp}xp → Lv{stat['level']} ({stat['xp']}/{stat['xp_to_next']})")

    return stats

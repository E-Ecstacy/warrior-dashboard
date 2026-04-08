"""Stat XP Distribution — 3 categories: body, mind, soul"""
 
def calculate_stat_xp(tier2, tier3):
    """Calculate XP for each stat based on activities"""
    stat_xp = {'body': 0, 'mind': 0, 'soul': 0}
 
    # ── BODY (physical training + mindful recovery) ───────────────────────────
    # Physical training  [was: strength]
    if tier2.get('full_workout'):    stat_xp['body'] += 25
    if tier2.get('light_exercise'):  stat_xp['body'] += 12
    if tier2.get('push_ups_100'):    stat_xp['body'] += 20
    if tier2.get('steps_10k'):       stat_xp['body'] += 8
    if tier2.get('stretching'):      stat_xp['body'] += 5
    if tier2.get('cold_shower'):     stat_xp['body'] += 3
 
    # Mindful recovery  [was: energy]
    if tier2.get('meditation'):      stat_xp['body'] += 8
    if tier2.get('gratitude'):       stat_xp['body'] += 3
    if tier2.get('breathwork'):      stat_xp['body'] += 5
    if tier2.get('nature_walk'):     stat_xp['body'] += 7
    if tier2.get('journal'):         stat_xp['body'] += 5
    if tier3.get('cold_exposure'):   stat_xp['body'] += 30
 
    # ── MIND (learning + focus + discipline) ──────────────────────────────────
    # Deep work & learning  [was: intellect]
    if tier2.get('deep_work'):       stat_xp['mind'] += 20
    if tier2.get('study_pomodoro'):  stat_xp['mind'] += 15
    if tier2.get('project_dev'):     stat_xp['mind'] += 18
    if tier2.get('part_time_job'):   stat_xp['mind'] += 20
    if tier2.get('new_skill'):       stat_xp['mind'] += 12
    if tier2.get('read_book'):       stat_xp['mind'] += 10
    if tier2.get('kinnu'):           stat_xp['mind'] += 8
    if tier2.get('online_course'):   stat_xp['mind'] += 15
    if tier2.get('code_practice'):   stat_xp['mind'] += 15
    if tier2.get('code_project'):    stat_xp['mind'] += 25
    if tier2.get('new_algorithm'):   stat_xp['mind'] += 60
 
    # Digital discipline  [was: discipline]
    if tier2.get('screen_under_2h'): stat_xp['mind'] += 15
    if tier2.get('screen_2_4h'):     stat_xp['mind'] += 8
    if tier2.get('no_phone_morning'):stat_xp['mind'] += 5
    if tier2.get('no_phone_night'):  stat_xp['mind'] += 5
    if tier2.get('plan_tomorrow'):   stat_xp['mind'] += 3
    if tier2.get('organize_space'):  stat_xp['mind'] += 5
    if tier2.get('budget_review'):   stat_xp['mind'] += 8
    if tier3.get('zero_screens'):    stat_xp['mind'] += 100
    if tier3.get('complete_todo'):   stat_xp['mind'] += 50
 
    # Boss moves  [was: intellect]
    if tier3.get('flow_state_4h'):   stat_xp['mind'] += 80
 
    # ── SOUL (social + influence) ─────────────────────────────────────────────
    # [was: influence — unchanged, just renamed]
    if tier2.get('meaningful_conversation'): stat_xp['soul'] += 8
    if tier2.get('help_code'):               stat_xp['soul'] += 10
    if tier2.get('call_family'):             stat_xp['soul'] += 5
    if tier2.get('group_activity'):          stat_xp['soul'] += 7
    if tier2.get('mentor_session'):          stat_xp['soul'] += 8
    if tier2.get('networking'):              stat_xp['soul'] += 6
    if tier2.get('compliment_someone'):      stat_xp['soul'] += 2
    if tier2.get('thank_someone'):           stat_xp['soul'] += 2
    if tier2.get('check_in'):               stat_xp['soul'] += 3
    if tier2.get('quality_time'):            stat_xp['soul'] += 10
    if tier3.get('teach_code'):              stat_xp['soul'] += 40
 
    return stat_xp
 
 
def update_stats(stats, stat_xp):
    """Update character stats with earned XP"""
    if not stats or not isinstance(stats, dict):
        stats = {}
 
    for stat_name, xp in stat_xp.items():
        if xp <= 0:
            continue
 
        stat = stats.get(stat_name, {'level': 1, 'xp': 0, 'xp_to_next': 100})
        stats[stat_name] = stat
 
        stat['xp'] += xp
 
        while stat['xp'] >= stat['xp_to_next']:
            stat['xp'] -= stat['xp_to_next']
            stat['level'] += 1
            stat['xp_to_next'] = int(100 * (1.2 ** (stat['level'] - 1)))
 
        print(f"  📊 {stat_name}: +{xp}xp → Lv{stat['level']} ({stat['xp']}/{stat['xp_to_next']})")
 
    return stats

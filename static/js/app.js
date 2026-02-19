// Warrior Dashboard - Frontend Logic

// State
let characterData = null;
let streaksData = null;

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Open quest modal
    document.getElementById('open-quest-modal').addEventListener('click', () => {
        document.getElementById('quest-modal').style.display = 'block';
    });
    
    // Close quest modal
    document.querySelector('.close').addEventListener('click', () => {
        document.getElementById('quest-modal').style.display = 'none';
    });
    
    // Open PR modal
    document.getElementById('open-pr-modal').addEventListener('click', () => {
        document.getElementById('pr-modal').style.display = 'block';
    });
    
    // Close PR modal
    document.querySelector('.close-pr').addEventListener('click', () => {
        document.getElementById('pr-modal').style.display = 'none';
    });
    
    // Open notes modal
    document.getElementById('open-notes-modal').addEventListener('click', () => {
        document.getElementById('notes-modal').style.display = 'block';
    });
    
    // Close notes modal
    document.querySelector('.close-notes').addEventListener('click', () => {
        document.getElementById('notes-modal').style.display = 'none';
    });
    
    // Open budget modal
    document.getElementById('open-budget-modal').addEventListener('click', () => {
        document.getElementById('budget-modal').style.display = 'block';
    });
    
    // Close budget modal
    document.querySelector('.close-budget').addEventListener('click', () => {
        document.getElementById('budget-modal').style.display = 'none';
    });
    
    // Open workout modal
    document.getElementById('open-workout-modal').addEventListener('click', () => {
        document.getElementById('workout-modal').style.display = 'block';
    });
    
    // Close workout modal
    document.querySelector('.close-workout').addEventListener('click', () => {
        document.getElementById('workout-modal').style.display = 'none';
    });
    
    // Close modals on outside click
    window.addEventListener('click', (e) => {
        const questModal = document.getElementById('quest-modal');
        const prModal = document.getElementById('pr-modal');
        const notesModal = document.getElementById('notes-modal');
        const budgetModal = document.getElementById('budget-modal');
        const workoutModal = document.getElementById('workout-modal');
        
        if (e.target === questModal) {
            questModal.style.display = 'none';
        }
        if (e.target === prModal) {
            prModal.style.display = 'none';
        }
        if (e.target === notesModal) {
            notesModal.style.display = 'none';
        }
        if (e.target === budgetModal) {
            budgetModal.style.display = 'none';
        }
        if (e.target === workoutModal) {
            workoutModal.style.display = 'none';
        }
    });
    
    // Form submissions
    document.getElementById('quest-form').addEventListener('submit', handleQuestSubmit);
    document.getElementById('pr-form').addEventListener('submit', handlePRSubmit);
    document.getElementById('notes-form').addEventListener('submit', handleNotesSubmit);
    document.getElementById('budget-form').addEventListener('submit', handleBudgetSubmit);
    document.getElementById('workout-form').addEventListener('submit', handleWorkoutSubmit);
    
    // Setup accordion functionality
    setupAccordions();
    
    // Update volume display in PR form
    const prInputs = ['weight', 'reps', 'sets'];
    prInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', updateVolumeDisplay);
        }
    });
    
    // Show/hide target date for goals
    const noteTypeRadios = document.querySelectorAll('input[name="note_type"]');
    noteTypeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            const targetDateGroup = document.getElementById('target-date-group');
            if (radio.value === 'goal') {
                targetDateGroup.style.display = 'block';
            } else {
                targetDateGroup.style.display = 'none';
            }
        });
    });
}

// Setup accordion toggle functionality
function setupAccordions() {
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    // Open all accordions by default
    document.querySelectorAll('.accordion-item').forEach(item => {
        item.classList.add('active');
    });
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const accordionItem = header.parentElement;
            const wasActive = accordionItem.classList.contains('active');
            
            // Optional: Close other accordions when opening one (comment out if you want multiple open)
            // document.querySelectorAll('.accordion-item').forEach(item => {
            //     item.classList.remove('active');
            // });
            
            // Toggle current accordion
            if (wasActive) {
                accordionItem.classList.remove('active');
            } else {
                accordionItem.classList.add('active');
            }
        });
    });
}

// Load dashboard data
async function loadDashboard() {
    try {
        // Load character stats
        const charResponse = await fetch('/api/character');
        characterData = await charResponse.json();
        updateCharacterDisplay();
        
        // Load streaks
        const streaksResponse = await fetch('/api/streaks');
        streaksData = await streaksResponse.json();
        updateStreaksDisplay();
        
        // Load achievements
        const achievementsResponse = await fetch('/api/achievements');
        const achievementsData = await achievementsResponse.json();
        updateAchievementsDisplay(achievementsData);
        
        // Load skill tree
        const skillTreeResponse = await fetch('/api/character');
        const fullData = await skillTreeResponse.json();
        updateSkillTreeDisplay(fullData);
        
        // Load today's summary if exists
        loadTodaySummary();
        
        // Load personal records
        loadPersonalRecords();
        
        // Load notes and plans
        loadNotes();
        
        // Load budget tracker
        loadBudget();
        
        // Load workout sessions
        loadWorkouts();
        
        // Load new features
        loadDailyChallenge();
        loadNemesisMode();
        loadGhostData();
        loadAnalytics();
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        alert('Error loading dashboard data. Please refresh the page.');
    }
}

// Update character display
function updateCharacterDisplay() {
    // Main stats
    document.getElementById('char-level').textContent = characterData.level;
    document.getElementById('total-points').textContent = characterData.total_points.toLocaleString();
    document.getElementById('week-points').textContent = characterData.current_week_points;
    
    // Individual stats
    const stats = ['strength', 'intellect', 'discipline', 'energy', 'influence'];
    stats.forEach(stat => {
        const statData = characterData.stats[stat];
        document.getElementById(`${stat}-level`).textContent = statData.level;
        document.getElementById(`${stat}-xp`).textContent = statData.xp;
        document.getElementById(`${stat}-next`).textContent = statData.xp_to_next;
        
        const progress = (statData.xp / statData.xp_to_next) * 100;
        document.getElementById(`${stat}-progress`).style.width = `${progress}%`;
    });
}

// Update streaks display
function updateStreaksDisplay() {
    const container = document.getElementById('streaks-container');
    container.innerHTML = '';
    
    const streakNames = {
        'no_porn': '🚫 No Porn',
        'workout': '💪 Workout',
        'sleep_7h': '😴 7+ Hours Sleep',
        'morning_routine': '🌅 Morning Routine',
        'no_doomscroll': '📵 No Doomscroll',
        'deep_work': '🎯 Deep Work',
        'reading': '📖 Reading',
        'screen_time_under_2h': '📱 Screen <2h',
        'meditation': '🧘 Meditation',
        'coding_practice': '💻 Code Practice'
    };
    
    for (const [key, streak] of Object.entries(streaksData)) {
        const card = document.createElement('div');
        card.className = 'streak-card';
        
        const multiplierText = streak.multiplier > 1 ? `${streak.multiplier}x multiplier` : '';
        const effectivePoints = streak.base_points * streak.multiplier;
        
        card.innerHTML = `
            <div class="streak-header">
                <span class="streak-name">${streakNames[key]}</span>
                <span class="streak-days">${streak.current} 🔥</span>
            </div>
            <div class="streak-multiplier">${multiplierText}</div>
            <div class="streak-points">Base: ${streak.base_points}p → ${Math.round(effectivePoints)}p</div>
            <div class="streak-points">Longest: ${streak.longest} days</div>
        `;
        
        container.appendChild(card);
    }
}

// Update achievements display
function updateAchievementsDisplay(data) {
    const container = document.getElementById('achievements-container');
    container.innerHTML = '';
    
    // Show earned achievements first
    data.earned.forEach(achievement => {
        const card = createAchievementCard(achievement, true);
        container.appendChild(card);
    });
    
    // Show available achievements (locked)
    data.available.slice(0, 6).forEach(achievement => {
        if (!data.earned.find(a => a.id === achievement.id)) {
            const card = createAchievementCard(achievement, false);
            container.appendChild(card);
        }
    });
}

function createAchievementCard(achievement, unlocked) {
    const card = document.createElement('div');
    card.className = `achievement-card ${unlocked ? 'unlocked' : 'locked'}`;
    
    const icon = unlocked ? '🏆' : '🔒';
    
    card.innerHTML = `
        <div class="achievement-header">
            <span class="achievement-icon">${icon}</span>
            <span class="achievement-name">${achievement.name}</span>
        </div>
        <div class="achievement-desc">${achievement.description}</div>
        <div class="achievement-bonus">+${achievement.points_bonus} points</div>
        ${unlocked && achievement.date_earned ? `<div class="achievement-date">Unlocked: ${achievement.date_earned}</div>` : ''}
    `;
    
    return card;
}

// Update skill tree display
function updateSkillTreeDisplay(data) {
    const container = document.getElementById('skill-tree-container');
    const skillTree = data.skill_tree || { locked: [], unlocked: [], available_points: 0 };
    
    document.getElementById('available-points').textContent = skillTree.available_points;
    container.innerHTML = '';
    
    // Show unlocked skills
    skillTree.unlocked.forEach(skill => {
        const card = createSkillCard(skill, true, skillTree.available_points);
        container.appendChild(card);
    });
    
    // Show locked skills
    skillTree.locked.forEach(skill => {
        const card = createSkillCard(skill, false, skillTree.available_points);
        container.appendChild(card);
    });
}

function createSkillCard(skill, unlocked, availablePoints) {
    const card = document.createElement('div');
    const tier = skill.cost === 500 ? 'bronze' : skill.cost === 1000 ? 'silver' : 'gold';
    card.className = `skill-card ${tier} ${unlocked ? 'unlocked' : 'locked'}`;
    
    card.innerHTML = `
        <div class="skill-header">
            <span class="skill-name">${unlocked ? '✅ ' : ''}${skill.name}</span>
            <span class="skill-cost">${skill.cost}p</span>
        </div>
        <div class="skill-desc">${skill.description || 'Unlock to reveal'}</div>
        ${unlocked && skill.date_unlocked ? `<div style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.85rem;">Unlocked: ${skill.date_unlocked}</div>` : ''}
    `;
    
    if (!unlocked && availablePoints >= skill.cost) {
        card.style.cursor = 'pointer';
        card.addEventListener('click', () => unlockSkill(skill.id));
    }
    
    return card;
}

// Unlock skill
async function unlockSkill(skillId) {
    if (!confirm('Are you sure you want to unlock this skill?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/skill-tree/unlock/${skillId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`🎉 Unlocked: ${result.skill.name}!`);
            loadDashboard(); // Reload to show updated points
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Error unlocking skill:', error);
        alert('Error unlocking skill. Please try again.');
    }
}

// Load today's summary
async function loadTodaySummary() {
    try {
        const response = await fetch('/api/daily-log');
        const logs = await response.json();
        
        const today = new Date().toISOString().split('T')[0];
        const todayLog = logs.find(log => log.date === today);
        
        if (todayLog) {
            document.getElementById('today-summary').style.display = 'block';
            document.getElementById('today-points').textContent = todayLog.total_points;
            
            const status = todayLog.total_points >= 100 ? '🏆 Victory' :
                          todayLog.total_points >= 50 ? '⚔️ Survival' : '❌ Defeat';
            document.getElementById('today-status').textContent = status;
        }
    } catch (error) {
        console.error('Error loading today summary:', error);
    }
}

// Handle quest form submission
async function handleQuestSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    // Build quest entry object
    const entry = {
        tier1_complete: false,
        tier2: {},
        tier3: {},
        streaks_completed: [],
        energy_score: parseInt(formData.get('energy_score')),
        notes: formData.get('notes'),
        penalty_gaming: formData.has('penalty_gaming')
    };
    
    // Tier 1
    const tier1Items = ['tier1_sleep', 'tier1_no_porn', 'tier1_focused', 'tier1_move'];
    entry.tier1_complete = tier1Items.every(item => formData.has(item));
    
    // Tier 2
    const tier2Activities = [
        'full_workout', 'light_exercise', 'push_ups_100', 'steps_10k', 'stretching', 'cold_shower',
        'deep_work', 'study_pomodoro', 'project_dev', 'part_time_job', 'new_skill',
        'read_book', 'kinnu', 'online_course', 'code_practice', 'journal',
        'screen_under_2h', 'screen_2_4h', 'no_phone_morning', 'no_phone_night',
        'plan_tomorrow', 'organize_space', 'budget_review',
        'meditation', 'gratitude', 'breathwork', 'nature_walk',
        'code_project', 'write_docs', 'build_design', 'open_source',
        'conversation', 'help_code', 'call_family'
    ];
    
    tier2Activities.forEach(activity => {
        if (formData.has(activity)) {
            entry.tier2[activity] = true;
        }
    });
    
    // Deep work quality
    if (entry.tier2.deep_work) {
        entry.tier2.deep_work_quality = formData.get('deep_work_quality');
    }
    
    // Tier 3
    const tier3Activities = [
        'flow_state_4h', 'zero_screens', 'complete_todo', 
        'cold_exposure', 'new_algorithm', 'teach_code'
    ];
    
    tier3Activities.forEach(activity => {
        if (formData.has(activity)) {
            entry.tier3[activity] = true;
        }
    });
    
    // Streaks
    const streakInputs = form.querySelectorAll('input[name^="streak_"]');
    streakInputs.forEach(input => {
        if (input.checked && input.value) {
            entry.streaks_completed.push(input.value);
        }
    });
    
    // Submit to API
    try {
        const response = await fetch('/api/daily-log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(entry)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Show achievements if any
            if (result.achievements && result.achievements.length > 0) {
                showAchievementPopup(result.achievements);
            }
            
            // Show appropriate success message
            let message = result.merged 
                ? `✅ Activities Added to Today!\n\n🎯 New Points This Session: ${result.total_points}\n💡 ${result.message}\n\n📊 All today's activities are now combined in one entry!`
                : `✅ Quest Complete!\n\n🎯 Total Points: ${result.total_points}\n\n💪 Keep building your character!`;
            
            alert(message);
            
            // Close modal and reload
            document.getElementById('quest-modal').style.display = 'none';
            form.reset();
            loadDashboard();
            
        } else {
            alert('Error submitting quest. Please try again.');
        }
    } catch (error) {
        console.error('Error submitting quest:', error);
        alert('Error submitting quest. Please check your connection.');
    }
}

// Show achievement popup
function showAchievementPopup(achievements) {
    const popup = document.getElementById('achievement-popup');
    const details = document.getElementById('achievement-details');
    
    details.innerHTML = achievements.map(a => `
        <div style="margin: 1rem 0; padding: 1rem; background: rgba(255, 214, 10, 0.1); border-radius: 10px;">
            <h3 style="color: var(--accent-gold); margin-bottom: 0.5rem;">${a.name}</h3>
            <p style="color: var(--text-secondary);">${a.description}</p>
            <p style="color: var(--accent-green); font-weight: bold; margin-top: 0.5rem;">+${a.points_bonus} bonus points!</p>
        </div>
    `).join('');
    
    popup.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        popup.style.display = 'none';
    }, 5000);
    
    // Click to close
    popup.addEventListener('click', () => {
        popup.style.display = 'none';
    });
}

// Helper: Get today's date in YYYY-MM-DD format
function getTodayDate() {
    return new Date().toISOString().split('T')[0];
}

// Load and display personal records
async function loadPersonalRecords() {
    try {
        const response = await fetch('/api/personal-records');
        const data = await response.json();
        
        const container = document.getElementById('pr-container');
        container.innerHTML = '';
        
        const exercises = data.exercises || {};
        const exerciseCount = Object.keys(exercises).length;
        
        if (exerciseCount === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">No PRs logged yet. Click "Log New PR" to get started!</p>';
            return;
        }
        
        // Sort exercises by volume (highest first)
        const sortedExercises = Object.entries(exercises).sort((a, b) => b[1].volume - a[1].volume);
        
        sortedExercises.forEach(([name, record]) => {
            const card = document.createElement('div');
            card.className = 'pr-card';
            
            const isRecent = (new Date() - new Date(record.date)) < 7 * 24 * 60 * 60 * 1000; // Within 7 days
            
            card.innerHTML = `
                ${isRecent ? '<div class="pr-badge">🔥 NEW</div>' : ''}
                <div class="pr-card-header">
                    <span class="pr-exercise-name">${name}</span>
                    <button class="pr-delete" onclick="deletePR('${name}')" title="Delete PR">🗑️</button>
                </div>
                <div class="pr-stats">
                    <div class="pr-stat">
                        <span class="pr-stat-label">Weight</span>
                        <span class="pr-stat-value">${record.weight}</span>
                    </div>
                    <div class="pr-stat">
                        <span class="pr-stat-label">Reps</span>
                        <span class="pr-stat-value">${record.reps}</span>
                    </div>
                    <div class="pr-stat">
                        <span class="pr-stat-label">Sets</span>
                        <span class="pr-stat-value">${record.sets}</span>
                    </div>
                </div>
                <div class="pr-volume">
                    <span class="pr-volume-label">Total Volume</span>
                    <span class="pr-volume-value">${record.volume.toLocaleString()}</span>
                </div>
                <div class="pr-date">📅 Set on ${record.date}</div>
            `;
            
            container.appendChild(card);
        });
        
    } catch (error) {
        console.error('Error loading personal records:', error);
    }
}

// Update volume display in PR form
function updateVolumeDisplay() {
    const weight = parseFloat(document.getElementById('weight').value) || 0;
    const reps = parseInt(document.getElementById('reps').value) || 0;
    const sets = parseInt(document.getElementById('sets').value) || 0;
    
    const volume = weight * reps * sets;
    document.getElementById('volume-display').textContent = volume.toLocaleString();
}

// Handle PR form submission
async function handlePRSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    const prData = {
        exercise_name: formData.get('exercise_name'),
        weight: parseFloat(formData.get('weight')),
        reps: parseInt(formData.get('reps')),
        sets: parseInt(formData.get('sets'))
    };
    
    try {
        const response = await fetch('/api/personal-records', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(prData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (result.is_pr) {
                const improvement = result.improvement_percent > 0 
                    ? ` (${result.improvement_percent}% improvement!)` 
                    : ' (First PR!)';
                
                alert(`🎉 NEW PERSONAL RECORD!\n\n💪 ${prData.exercise_name}\n📊 Volume: ${result.new_volume.toLocaleString()}${improvement}\n⭐ Points Earned: +${result.points_earned}p\n\nKeep crushing it!`);
            } else {
                alert(`📝 Logged, but not a PR yet.\n\nCurrent PR: ${result.old_volume.toLocaleString()}\nYour volume: ${result.new_volume.toLocaleString()}\n\nKeep pushing!`);
            }
            
            // Close modal and reload
            document.getElementById('pr-modal').style.display = 'none';
            form.reset();
            updateVolumeDisplay();
            loadDashboard();
            
        } else {
            alert('Error logging PR: ' + result.error);
        }
    } catch (error) {
        console.error('Error submitting PR:', error);
        alert('Error submitting PR. Please try again.');
    }
}

// Delete a PR
async function deletePR(exerciseName) {
    if (!confirm(`Are you sure you want to delete the PR for "${exerciseName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/personal-records', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ exercise_name: exerciseName })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ Deleted PR for ${exerciseName}`);
            loadPersonalRecords();
        } else {
            alert('Error deleting PR: ' + result.error);
        }
    } catch (error) {
        console.error('Error deleting PR:', error);
        alert('Error deleting PR. Please try again.');
    }
}

// Load and display notes and plans
async function loadNotes() {
    try {
        const response = await fetch('/api/notes');
        const data = await response.json();
        
        // Display plans
        const plansContainer = document.getElementById('plans-list');
        plansContainer.innerHTML = '';
        
        const activePlans = data.plans || [];
        
        if (activePlans.length === 0) {
            plansContainer.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">No active plans yet. Create one to earn points!</p>';
        } else {
            activePlans.forEach(plan => {
                const card = document.createElement('div');
                card.className = `plan-card ${plan.completed ? 'completed' : ''}`;
                
                const typeLabel = plan.type === 'tomorrow_plan' ? 'Tomorrow' : 'Goal';
                const categoryColors = {
                    'work': '#00d9ff',
                    'fitness': '#ff3864',
                    'learning': '#a855f7',
                    'coding': '#00ff87',
                    'personal': '#ffd60a',
                    'general': '#b0b0b0'
                };
                const categoryColor = categoryColors[plan.category] || '#b0b0b0';
                
                card.innerHTML = `
                    <div class="plan-header">
                        <span class="plan-category" style="background: ${categoryColor}33; color: ${categoryColor};">${plan.category}</span>
                        <span class="plan-type-badge">${typeLabel}</span>
                        <div class="plan-actions">
                            ${!plan.completed ? `<button class="plan-complete" onclick="completePlan(${plan.id})" title="Mark as done">✅</button>` : ''}
                            <button class="plan-delete" onclick="deleteNote(${plan.id}, 'plan')" title="Delete">🗑️</button>
                        </div>
                    </div>
                    <div class="plan-content">${plan.content}</div>
                    <div class="plan-date">
                        ${plan.completed ? `✅ Completed: ${plan.completed_date}` : `📅 Target: ${plan.target_date || 'Tomorrow'}`}
                    </div>
                `;
                
                plansContainer.appendChild(card);
            });
        }
        
        // Display recent notes
        const notesContainer = document.getElementById('notes-list');
        notesContainer.innerHTML = '';
        
        const recentNotes = data.daily_notes || [];
        
        if (recentNotes.length === 0) {
            notesContainer.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">No notes yet. Start journaling to earn points!</p>';
        } else {
            recentNotes.slice(-10).reverse().forEach(note => {
                const card = document.createElement('div');
                card.className = 'note-card';
                
                const typeIcons = {
                    'daily_note': '📔',
                    'idea': '💡'
                };
                const icon = typeIcons[note.type] || '📝';
                
                const typeLabels = {
                    'daily_note': 'Daily Note',
                    'idea': 'Idea'
                };
                const typeLabel = typeLabels[note.type] || 'Note';
                
                const categoryColors = {
                    'work': '#00d9ff',
                    'fitness': '#ff3864',
                    'learning': '#a855f7',
                    'coding': '#00ff87',
                    'personal': '#ffd60a',
                    'general': '#b0b0b0'
                };
                const categoryColor = categoryColors[note.category] || '#b0b0b0';
                
                card.innerHTML = `
                    <div class="note-header">
                        <span class="note-category" style="background: ${categoryColor}33; color: ${categoryColor};">${icon} ${note.category}</span>
                        <span class="note-type-badge">${typeLabel}</span>
                        <div class="note-actions">
                            <button class="note-delete" onclick="deleteNote(${note.id}, 'note')" title="Delete">🗑️</button>
                        </div>
                    </div>
                    <div class="note-content">${note.content}</div>
                    <div class="note-date">📅 ${note.date}</div>
                `;
                
                notesContainer.appendChild(card);
            });
        }
        
    } catch (error) {
        console.error('Error loading notes:', error);
    }
}

// Handle notes form submission
async function handleNotesSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    const noteData = {
        type: formData.get('note_type'),
        content: formData.get('content'),
        category: formData.get('category'),
        target_date: formData.get('target_date') || null
    };
    
    try {
        const response = await fetch('/api/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(noteData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            const typeMessages = {
                'daily_note': '📔 Daily Note saved!',
                'tomorrow_plan': '🎯 Tomorrow\'s plan created!',
                'goal': '🏆 Goal set!',
                'idea': '💡 Idea captured!'
            };
            
            const message = typeMessages[result.note_type] || 'Saved!';
            alert(`✅ ${message}\n\n⭐ Points Earned: +${result.points_earned}p\n\nKeep building momentum!`);
            
            // Close modal and reload
            document.getElementById('notes-modal').style.display = 'none';
            form.reset();
            loadDashboard();
            
        } else {
            alert('Error saving: ' + result.error);
        }
    } catch (error) {
        console.error('Error submitting note:', error);
        alert('Error saving. Please try again.');
    }
}

// Complete a plan
async function completePlan(planId) {
    try {
        const response = await fetch(`/api/notes/complete-plan/${planId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`🎉 Plan Completed!\n\n✅ Bonus Points: +${result.bonus_points}p\n\nGreat work following through!`);
            loadDashboard();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error completing plan:', error);
        alert('Error completing plan. Please try again.');
    }
}

// Delete a note or plan
async function deleteNote(id, type) {
    if (!confirm(`Are you sure you want to delete this ${type}?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/notes', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: id, type: type })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ Deleted ${type}`);
            loadNotes();
        } else {
            alert('Error deleting: ' + result.error);
        }
    } catch (error) {
        console.error('Error deleting:', error);
        alert('Error deleting. Please try again.');
    }
}

// Load daily challenge
async function loadDailyChallenge() {
    try {
        const response = await fetch('/api/daily-challenge');
        const challenge = await response.json();
        
        const container = document.getElementById('challenge-card');
        
        if (challenge.completed) {
            container.innerHTML = `
                <div class="challenge-completed">
                    <span class="challenge-completed-badge">✅</span>
                    <h3 style="text-align: center; color: var(--accent-green);">Challenge Completed!</h3>
                    <p style="text-align: center; color: var(--text-secondary);">${challenge.current_challenge.name}</p>
                    <p style="text-align: center; color: var(--accent-green); font-weight: bold;">+${challenge.current_challenge.points} points earned</p>
                    <p style="text-align: center; color: var(--text-dim); margin-top: 1rem;">New challenge tomorrow!</p>
                </div>
            `;
        } else if (challenge.current_challenge) {
            const ch = challenge.current_challenge;
            container.innerHTML = `
                <div class="challenge-header">
                    <span class="challenge-name">${ch.name}</span>
                    <span class="challenge-points">+${ch.points}p</span>
                </div>
                <p class="challenge-description">${ch.description}</p>
                <button class="challenge-complete-btn" onclick="completeDailyChallenge()">
                    ✅ Complete Challenge
                </button>
            `;
        }
    } catch (error) {
        console.error('Error loading daily challenge:', error);
    }
}

// Complete daily challenge
async function completeDailyChallenge() {
    if (!confirm('Did you actually complete this challenge?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/daily-challenge/complete', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`🎉 CHALLENGE COMPLETE!\n\n${result.challenge.name}\n\n⭐ +${result.points_earned} points!\n\nKeep crushing it!`);
            loadDashboard();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error completing challenge:', error);
        alert('Error completing challenge. Please try again.');
    }
}

// Load nemesis mode status
async function loadNemesisMode() {
    try {
        const response = await fetch('/api/nemesis-mode');
        const nemesis = await response.json();
        
        const container = document.getElementById('nemesis-container');
        
        if (nemesis.active) {
            container.innerHTML = `
                <div class="nemesis-active">
                    <h3 style="color: var(--accent-red); margin-bottom: 1rem;">⚠️ NEMESIS MODE ACTIVE</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 1rem;">Break ANY non-negotiable = ZERO points for the day</p>
                    
                    <div class="non-negotiables-list">
                        ${nemesis.non_negotiables.map(nn => `<span class="non-negotiable-badge">${nn.replace('_', ' ').toUpperCase()}</span>`).join('')}
                    </div>
                    
                    <div class="nemesis-gauge-container">
                        <p style="color: var(--text-secondary); margin-bottom: 0.5rem;">Nemesis Gauge:</p>
                        <div class="nemesis-gauge">
                            <div class="nemesis-gauge-fill" style="width: ${nemesis.nemesis_gauge}%"></div>
                            <span class="nemesis-gauge-text">${nemesis.nemesis_gauge}%</span>
                        </div>
                        <p style="color: var(--text-dim); font-size: 0.85rem; margin-top: 0.5rem;">
                            ${nemesis.nemesis_gauge >= 100 ? '💀 FORCED REST DAY INCOMING!' : `${100 - nemesis.nemesis_gauge}% until forced rest day`}
                        </p>
                    </div>
                    
                    <p style="color: var(--text-secondary); margin-top: 1rem;">Breaks this month: ${nemesis.breaks_this_month}</p>
                    
                    <button class="nemesis-activate-btn" onclick="deactivateNemesis()" style="margin-top: 1rem; background: var(--text-dim);">
                        Deactivate Nemesis Mode
                    </button>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="nemesis-inactive">
                    <h3 style="color: var(--accent-red); margin-bottom: 1rem;">💀 NEMESIS MODE</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 1rem;">Real stakes. Real consequences.</p>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Choose 3 non-negotiables. Break one = Zero points for the day.</p>
                    <button class="nemesis-activate-btn" onclick="alert('Nemesis activation modal coming soon! For now, use API directly.')">
                        ⚠️ Activate Nemesis Mode
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading nemesis mode:', error);
    }
}

// Load ghost data
async function loadGhostData() {
    try {
        const response = await fetch('/api/ghost-data');
        const ghost = await response.json();
        
        const container = document.getElementById('ghost-container');
        
        if (ghost.has_ghost) {
            const vsData = ghost.today_vs_last_week;
            container.innerHTML = `
                <div class="ghost-card">
                    <h3 style="margin-bottom: 1.5rem; text-align: center;">Today vs Last Week</h3>
                    <div class="ghost-vs">
                        <div class="ghost-you">
                            <p class="ghost-label">You Today</p>
                            <p class="ghost-score ${vsData.winning ? 'winning' : 'losing'}">${vsData.today}</p>
                        </div>
                        <span class="ghost-vs-divider">⚔️</span>
                        <div class="ghost-shadow">
                            <p class="ghost-label">Ghost (Last Week)</p>
                            <p class="ghost-score">${vsData.last_week}</p>
                        </div>
                    </div>
                    <p style="text-align: center; color: ${vsData.winning ? 'var(--accent-green)' : 'var(--accent-red)'}; font-weight: bold; margin-top: 1rem;">
                        ${vsData.winning ? '🏆 You\'re winning! +' : '📉 Behind by '} ${Math.abs(vsData.difference)} points
                    </p>
                </div>
                
                <div class="ghost-card">
                    <h3 style="margin-bottom: 1rem;">📊 Your Records</h3>
                    <div class="analytics-stat-row">
                        <span class="analytics-stat-label">Weekly Average:</span>
                        <span class="analytics-stat-value">${ghost.weekly_average}p</span>
                    </div>
                    <div class="analytics-stat-row">
                        <span class="analytics-stat-label">Best Week Ever:</span>
                        <span class="analytics-stat-value">${ghost.best_week}p</span>
                    </div>
                    <div class="analytics-stat-row">
                        <span class="analytics-stat-label">Total Days:</span>
                        <span class="analytics-stat-value">${ghost.total_days}</span>
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="ghost-card" style="text-align: center; padding: 3rem;">
                    <p style="color: var(--text-secondary); font-size: 1.1rem;">👻 Ghost data will appear after 7 days of logging</p>
                    <p style="color: var(--text-dim); margin-top: 1rem;">Keep logging to unlock comparisons!</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading ghost data:', error);
    }
}

// Load analytics
async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        const analytics = await response.json();
        
        const container = document.getElementById('analytics-container');
        
        if (analytics.total_days === 0) {
            container.innerHTML = `
                <div class="analytics-card" style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                    <p style="color: var(--text-secondary); font-size: 1.1rem;">📊 Analytics will appear after logging your first day</p>
                </div>
            `;
            return;
        }
        
        // Overview stats
        const overviewHTML = `
            <div class="analytics-card">
                <h3>📈 Overview</h3>
                <div class="analytics-stat-row">
                    <span class="analytics-stat-label">Total Days:</span>
                    <span class="analytics-stat-value">${analytics.total_days}</span>
                </div>
                <div class="analytics-stat-row">
                    <span class="analytics-stat-label">Average/Day:</span>
                    <span class="analytics-stat-value">${analytics.average_points}p</span>
                </div>
                <div class="analytics-stat-row">
                    <span class="analytics-stat-label">Best Day:</span>
                    <span class="analytics-stat-value" style="color: var(--accent-green)">${analytics.best_day}p</span>
                </div>
                <div class="analytics-stat-row">
                    <span class="analytics-stat-label">Worst Day:</span>
                    <span class="analytics-stat-value" style="color: var(--accent-red)">${analytics.worst_day}p</span>
                </div>
                <div class="analytics-stat-row">
                    <span class="analytics-stat-label">Total Points:</span>
                    <span class="analytics-stat-value">${analytics.total_points}</span>
                </div>
            </div>
        `;
        
        // Activity breakdown
        const activities = Object.entries(analytics.activity_breakdown).sort((a, b) => b[1] - a[1]).slice(0, 10);
        const maxCount = activities[0] ? activities[0][1] : 1;
        const activityHTML = `
            <div class="analytics-card">
                <h3>🎯 Top Activities</h3>
                <div class="activity-breakdown-list">
                    ${activities.map(([activity, count]) => `
                        <div class="activity-item">
                            <span>${activity.replace(/_/g, ' ')}</span>
                            <span style="color: var(--accent-cyan); font-weight: bold;">${count}x</span>
                        </div>
                        <div class="activity-bar">
                            <div class="activity-bar-fill" style="width: ${(count / maxCount) * 100}%"></div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Weekly trend
        const trendHTML = analytics.weekly_trend.length > 0 ? `
            <div class="analytics-card" style="grid-column: 1 / -1;">
                <h3>📊 Weekly Trend</h3>
                <div class="weekly-trend-chart">
                    ${analytics.weekly_trend.map(week => {
                        const maxPoints = Math.max(...analytics.weekly_trend.map(w => w.points));
                        const height = (week.points / maxPoints) * 100;
                        return `
                            <div class="trend-bar" style="height: ${height}%">
                                <span class="trend-bar-label">Week ${week.week}</span>
                                <span class="trend-bar-value">${week.points}p</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        ` : '';
        
        // Best day of week
        const dayHTML = analytics.best_day_of_week ? `
            <div class="analytics-card">
                <h3>🗓️ Best Day of Week</h3>
                <p style="text-align: center; font-size: 2rem; color: var(--accent-green); margin: 1rem 0;">${analytics.best_day_of_week}</p>
                <p style="text-align: center; color: var(--text-secondary);">You perform best on ${analytics.best_day_of_week}s</p>
            </div>
        ` : '';
        
        container.innerHTML = overviewHTML + activityHTML + trendHTML + dayHTML;
        
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Budget Functions
async function loadBudget() {
    try {
        const response = await fetch('/api/budget');
        const data = await response.json();
        
        const container = document.getElementById('budget-overview');
        
        container.innerHTML = `
            <div class="budget-balance">
                <h3>Balance: $${data.balance.toFixed(2)}</h3>
            </div>
            <div class="budget-summary">
                <p>This Month - Income: $${data.monthly_income.toFixed(2)} | Expenses: $${data.monthly_expenses.toFixed(2)}</p>
            </div>
            <div class="transactions">
                <h4>Recent Transactions:</h4>
                ${data.transactions.length > 0 ? data.transactions.slice(-10).reverse().map(t => `
                    <div class="transaction ${t.type}">
                        ${t.date} - ${t.category}: ${t.type === 'income' ? '+' : '-'}$${t.amount.toFixed(2)}
                        ${t.description ? `(${t.description})` : ''}
                    </div>
                `).join('') : '<p style="text-align: center; color: var(--text-secondary);">No transactions yet. Add your first transaction!</p>'}
            </div>
        `;
    } catch (error) {
        console.error('Error loading budget:', error);
    }
}

async function handleBudgetSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/api/budget', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                action: 'add_transaction',
                type: formData.get('type'),
                amount: formData.get('amount'),
                category: formData.get('category'),
                description: formData.get('description'),
                date: new Date().toISOString().split('T')[0]
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ Transaction Added!\n\nNew Balance: $${result.new_balance.toFixed(2)}\n+${result.points_earned} points earned for tracking!`);
            document.getElementById('budget-modal').style.display = 'none';
            form.reset();
            loadDashboard();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error adding transaction. Please try again.');
    }
}

// Workout Functions  
async function loadWorkouts() {
    try {
        const response = await fetch('/api/workouts');
        const data = await response.json();
        
        const container = document.getElementById('workout-container');
        
        container.innerHTML = `
            <h4>Recent Sessions:</h4>
            ${data.history.length > 0 ? data.history.slice(-10).reverse().map(s => `
                <div class="workout-card">
                    <strong>${s.template_name || 'Custom Workout'}</strong> - ${s.date}
                    <br>📋 ${s.exercises_completed.length} exercises | ⏱️ ${s.duration_minutes} min
                    ${s.notes ? `<br><em>"${s.notes}"</em>` : ''}
                </div>
            `).join('') : '<p style="text-align: center; color: var(--text-secondary);">No workouts logged yet. Log your first session!</p>'}
        `;
    } catch (error) {
        console.error('Error loading workouts:', error);
    }
}

async function handleWorkoutSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    const exercises = formData.get('exercises').split('\n').filter(e => e.trim()).map(e => ({name: e.trim()}));
    
    try {
        const response = await fetch('/api/workouts', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                action: 'log_session',
                template_name: formData.get('name'),
                exercises_completed: exercises,
                duration_minutes: parseInt(formData.get('duration')),
                notes: formData.get('notes'),
                date: new Date().toISOString().split('T')[0]
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`💪 Workout Logged!\n\n🎯 ${result.points_earned} points earned!\n\n${exercises.length} exercises completed in ${formData.get('duration')} minutes.\n\nKeep crushing it!`);
            document.getElementById('workout-modal').style.display = 'none';
            form.reset();
            loadDashboard();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error logging workout. Please try again.');
    }
}
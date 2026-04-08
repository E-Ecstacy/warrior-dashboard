# ⚔️ Warrior Dashboard
 
> Turn your daily discipline into an RPG. Log habits, earn XP, level up stats, unlock real rewards.
 
**Live demo:** [warrior-dashboard.onrender.com](https://warrior-dashboard.onrender.com)
 
---
 
## What it is
 
Warrior Dashboard is a self-hosted gamification system for self-improvement. Instead of a boring habit tracker, every action you take earns points and XP toward five character stats. Maintain streaks, trigger combos, unlock skill tree rewards, and face your Nemesis if you break your non-negotiables.
 
Built by a 15-year-old in London. Started as vibe-coded spaghetti, refactored from scratch after learning C fundamentals.
 
---
 
## Features
 
| Feature | What it does |
|--------|-------------|
| 🎯 Daily Quest | Log activities across 5 stat categories, earn points and XP |
| 📊 Character Stats | Body, Mind and Soul — each levels up independently |
| 🔥 Streaks | Per-habit streaks with XP multipliers at 7, 14, and 30 days |
| 🗺️ Warrior Roadmap | 24-trait daily checklist grouped into Foundation, Identity, Skills, Body, Wealth |
| ⚡ Daily Challenge | Random bonus challenge generated every day |
| 🌳 Skill Tree | Spend points to unlock real-life rewards you define |
| 🏆 Achievements | Six milestones that unlock automatically |
| 😈 Nemesis Mode | Break a non-negotiable = all points zeroed for the day |
| 💰 Budget Tracker | Log income and expenses, earn points for staying on top of finances |
| 💻 Coding Tracker | Track programming sessions per language with XP and leveling |
| 📈 Analytics | Weekly trends, top activities, best/worst days |
| 👻 Ghost Mode | Compare this week vs your best week |
 
---
 
## Tech Stack
 
- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Login
- **Database:** PostgreSQL (production) / SQLite (local)
- **Frontend:** Jinja2, vanilla CSS and JS — no framework
- **Auth:** Werkzeug password hashing
- **Hosting:** Render + Gunicorn
 
---
 
## Quick Start
 
```bash
git clone https://github.com/E-Ecstacy/warrior-dashboard.git
cd warrior-dashboard
git checkout refactored
pip install -r requirements.txt
python run.py
```
 
Visit `http://localhost:5000`, register, and start your first quest.
 
---
 
## Environment Variables
 
| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-key-change-in-production` | Change this in production |
| `DATABASE_URL` | `sqlite:///warrior.db` | Set to PostgreSQL URI in production |
 
---
 
## Project Structure
 
```
warrior-dashboard/
├── app/
│   ├── __init__.py        # App factory
│   ├── models.py          # User, Character, DailyLog, RoadmapEntry
│   ├── routes/
│   │   ├── main.py        # Dashboard routes
│   │   ├── auth.py        # Login / register
│   │   └── roadmap.py     # Warrior Roadmap routes
│   ├── features/          # Points, stats, streaks, combos, leveling
│   ├── constants/
│   │   └── traits.py      # 24 roadmap trait definitions
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── partials/
│       └── roadmap/
├── config.py
├── requirements.txt
└── run.py
```
 
---
 
## License
 
MIT — build your own character arc.
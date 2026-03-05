# ⚔️ Warrior Dashboard

> *"This isn't a schedule. This is your character arc."*

A self-improvement RPG built with Flask. Track your daily habits, earn points, level up your character stats, and unlock real-life rewards — all through a gamified dashboard that turns discipline into a game you actually want to play.

---

## 📸 Overview

Warrior Dashboard turns your daily routine into an RPG. Complete workouts, deep work sessions, and good habits to earn XP and points. Level up five character stats. Maintain streaks. Unlock rewards. Face your Nemesis.

---

## ✨ Features

### 🎯 Daily Quest Log
Log your activities each day across five stat categories. Every action earns points and XP toward your character stats. Submit your quest at the end of the day and watch your character grow.

### 📊 Five Character Stats
Each activity contributes XP to one or more of your core stats:

| Stat | Icon | Powered by |
|------|------|-----------|
| Strength | ⚔️ | Workouts, push-ups, cold showers |
| Intellect | 🧠 | Deep work, reading, coding, courses |
| Discipline | 🛡️ | Screen limits, planning, organization |
| Energy | ⚡ | Meditation, breathwork, nature walks |
| Influence | 👑 | Teaching, networking, quality time |

Stats level up with XP, displayed with progress bars on the main dashboard.

### 🔥 Streaks
Maintain daily habits to build streaks with multipliers. Active streaks are tracked for:
- No Porn
- Workout
- Meditation & Deep Work
- Reading & Coding Practice
- Sleep 7h+, Morning Routine
- No Doomscroll, Screen Time < 2h

### ⚡ Daily Challenge
A random challenge is generated every day — things like *"No Caffeine Today"*, *"100 Burpees"*, or *"Don't Complain All Day"*. Complete it for bonus points. Categories range from Discipline to Strength to Influence.

### 🌳 Skill Tree
Spend accumulated points to unlock real-life rewards you define. Examples include:
- **Advanced Workout Program** — 500p
- **Weekend Experience / Trip** — 1000p
- **Professional Certification** — 2500p
- **Major Dream Purchase** — 2500p

Points are spent, not just tracked — making rewards feel genuinely earned.

### 🏆 Achievements
Six achievements that unlock automatically when you hit milestones:

| Achievement | Condition | Bonus |
|------------|-----------|-------|
| Week Warrior | 7 days of 100+ points | +50p |
| Balanced Life | All 5 stats hit in a week | +50p |
| Comeback Kid | 200+ points after a bad day | +30p |
| Flow State Master | 4h+ deep work in one session | +80p |
| Digital Monk | Zero screens all day | +100p |
| Streak Legend | 30-day streak on any habit | +100p |

### 📝 Notes & Plans
- **Notes** — Quick reflections and ideas, +2p each
- **Plans** — Tomorrow's goals and tasks, +5p to write, +3p when completed

### 💰 Budget Tracker
Log income and expenses with categories. Tracks your monthly balance, income vs. expenses, and recent transactions. Every entry earns +2p for staying on top of your finances.

### 💻 Coding Skill Tree
Track programming sessions per language with XP and leveling:
- Languages: Python, JavaScript, C, Other
- Task types: Practice, Project, Tutorial, Problem Solving
- XP multipliers reward harder work (Problem Solving = 2x)
- Bonus points for sessions over 60 or 120 minutes

### 😈 Nemesis Mode
The hardcore accountability system. Choose one or more non-negotiable habits. If you break any of them on a given day, **all your points for that day are zeroed**. A Nemesis Gauge tracks repeated failures — reach 100% and face a forced rest day.

### 📈 Analytics
After enough days of logging, unlock insights:
- Total days logged, average points, best and worst days
- Top 8 most-completed activities with visual bars
- Weekly trend — last 4 weeks compared

### 📜 History
A log of every day you've submitted, with points earned, Tier 1 completion, and any combos triggered.

### ⚡ Combo System
Certain combinations of activities on the same day trigger combo bonuses — extra points for going above and beyond.

---

## 🏗️ Tech Stack

- **Backend:** Python 3.12, Flask 3, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite (single file, zero config)
- **Frontend:** Jinja2 server-side rendering, vanilla CSS/JS — no frontend framework
- **Auth:** Werkzeug password hashing
- **Deployment:** Gunicorn + Docker

---

## 🚀 Quick Start

### Option 1 — Run locally

```bash
# Clone the repo
git clone https://github.com/your-username/warrior-dashboard.git
cd warrior-dashboard

# Install dependencies
pip install -r requirements.txt

# Run
python run.py
```

Visit `http://localhost:5000`, register an account, and start your first quest.

### Option 2 — Docker

```bash
# From the project root
cd docker
docker compose up --build
```

Visit `http://localhost:5000`. The SQLite database is persisted in a Docker volume so your data survives container restarts.

To stop:
```bash
docker compose down
```

---

## 📁 Project Structure

```
warrior-dashboard/
├── app/
│   ├── __init__.py           # App factory
│   ├── models.py             # SQLAlchemy models (User, Character, DailyLog)
│   ├── routes/
│   │   ├── main.py           # All dashboard routes
│   │   └── auth.py           # Login / register / logout
│   ├── features/
│   │   ├── points.py         # Point calculation logic
│   │   ├── stats.py          # Stat XP distribution
│   │   ├── streaks.py        # Streak tracking
│   │   ├── combos.py         # Combo detection
│   │   ├── leveling.py       # Level up thresholds
│   │   └── character_init.py # Default character data
│   ├── templates/
│   │   ├── base.html         # Layout, CSS, JS
│   │   ├── index.html        # Dashboard (assembles partials)
│   │   ├── partials/         # One file per tab/section
│   │   └── auth/             # Login and register pages
│   └── static/
│       └── css/style.css
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── config.py
├── requirements.txt
└── run.py
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-key-change-in-production` | Flask session secret — **change this in production** |
| `DATABASE_URL` | `sqlite:///warrior.db` | Database URI |
| `FLASK_ENV` | `development` | `development` or `production` |

---

## 📄 License

MIT — do whatever you want with it. Build your own character arc.
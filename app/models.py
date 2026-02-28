"""Database Models"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    character = db.relationship('Character', backref='user', uselist=False)
    logs = db.relationship('DailyLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
    level = db.Column(db.Integer, default=1)
    total_points = db.Column(db.Integer, default=0)
    current_week_points = db.Column(db.Integer, default=0)
    
    # JSON fields for complex data
    stats = db.Column(db.JSON, default=dict)
    streaks = db.Column(db.JSON, default=dict)
    achievements = db.Column(db.JSON, default=list)
    skill_tree = db.Column(db.JSON, default=dict)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DailyLog(db.Model):
    __tablename__ = 'daily_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    
    total_points = db.Column(db.Integer, default=0)
    tier1_complete = db.Column(db.Boolean, default=False)
    tier2 = db.Column(db.JSON, default=dict)
    tier3 = db.Column(db.JSON, default=dict)
    
    combos = db.Column(db.JSON, default=list)
    combo_bonus = db.Column(db.Integer, default=0)
    
    notes = db.Column(db.Text)
    energy_score = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)

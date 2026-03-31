"""Application Configuration"""
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    uri = os.getenv('DATABASE_URL', 'sqlite:///warrior.db')
    if uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)

class Development(Config):
    DEBUG = True

class Production(Config):
    DEBUG = False

config = {'development': Development, 'production': Production, 'default': Development}

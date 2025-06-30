import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret-jwt-key'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Ensure DATABASE_URL is set in the production environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


# Dictionary to access config classes by name
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

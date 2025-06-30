import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# The .env file is primarily for local development
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Use the JWT_SECRET_KEY from environment variables for security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # In production, the DATABASE_URL must be set in the environment.
    # Render will provide this automatically for its managed database.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL is not set for production environment!")


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

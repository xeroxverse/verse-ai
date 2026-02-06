"""
Configuration settings for AI Gaming Assistant
"""

import os

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Assistant settings
    MAX_CONVERSATION_HISTORY = 20  # Maximum messages to keep in memory
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 500
    
    # Supported games (can be expanded)
    SUPPORTED_GAMES = [
        'General Gaming',
        'Minecraft',
        'League of Legends',
        'Valorant',
        'Counter-Strike',
        'Dota 2',
        'Fortnite',
        'Apex Legends',
        'Overwatch',
        'Hearthstone',
        'World of Warcraft',
        'Elden Ring',
        'Dark Souls',
        'The Witcher 3',
        'Cyberpunk 2077',
        'GTA V',
        'Red Dead Redemption 2',
        'Baldur\'s Gate 3',
        'Starcraft 2',
        'Civilization VI',
        'FIFA/FC',
        'NBA 2K',
        'Rocket League',
        'Among Us',
        'Fall Guys',
        'Roblox',
    ]


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

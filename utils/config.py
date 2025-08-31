"""
Configuration utilities for the Discord bot
"""

import os
from typing import Optional

class Config:
    """Configuration class for bot settings"""
    
    # Bot settings
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
    
    # Discord settings
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Rate limiting settings
    RATE_LIMIT_MESSAGES = int(os.getenv('RATE_LIMIT_MESSAGES', '5'))
    RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', '60'))  # seconds
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    # Message settings
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '2000'))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.DISCORD_TOKEN:
            print("Error: DISCORD_TOKEN environment variable is required")
            return False
        
        return True
    
    @classmethod
    def get_env_example(cls) -> str:
        """Generate example .env file content"""
        return """# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here

# Optional Configuration
COMMAND_PREFIX=!
RATE_LIMIT_MESSAGES=5
RATE_LIMIT_PERIOD=60
LOG_LEVEL=INFO
LOG_FILE=bot.log
MAX_MESSAGE_LENGTH=2000
"""

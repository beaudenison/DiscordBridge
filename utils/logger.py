"""
Logging utilities for the Discord bot
"""

import logging
import sys
from datetime import datetime
import os

def setup_logger(name: str = 'CrossServerBot', level: str = 'INFO') -> logging.Logger:
    """
    Set up a logger with both file and console handlers
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(levelname)s | %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    log_file = os.getenv('LOG_FILE', 'bot.log')
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")
    
    # Discord.py logger configuration
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)
    
    # HTTP logger (reduce noise)
    http_logger = logging.getLogger('discord.http')
    http_logger.setLevel(logging.WARNING)
    
    return logger

def log_command_usage(logger: logging.Logger, ctx, command_name: str, success: bool = True):
    """
    Log command usage for monitoring and debugging
    
    Args:
        logger: Logger instance
        ctx: Discord command context
        command_name: Name of the command used
        success: Whether the command succeeded
    """
    status = "SUCCESS" if success else "FAILED"
    logger.info(
        f"COMMAND {status} | {command_name} | "
        f"User: {ctx.author} ({ctx.author.id}) | "
        f"Guild: {ctx.guild.name} ({ctx.guild.id}) | "
        f"Channel: {ctx.channel.name} ({ctx.channel.id})"
    )

def log_cross_server_message(logger: logging.Logger, from_server: str, to_server: str, 
                           author: str, message_preview: str):
    """
    Log cross-server message for audit purposes
    
    Args:
        logger: Logger instance
        from_server: Source server name
        to_server: Target server name
        author: Message author
        message_preview: First 50 characters of message
    """
    preview = message_preview[:50] + "..." if len(message_preview) > 50 else message_preview
    logger.info(
        f"CROSS-SERVER MESSAGE | {from_server} → {to_server} | "
        f"Author: {author} | Preview: {preview}"
    )

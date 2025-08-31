# Discord Cross-Server Messaging Bot

## Overview

This project is a Discord bot built with Python and discord.py that enables seamless messaging between multiple Discord servers. The bot allows users to send messages from one Discord server to another, creating a bridge for cross-server communication. It features rich embed formatting, rate limiting protection, comprehensive error handling, and administrator controls for server configuration.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **discord.py 2.6.2**: Modern Discord API wrapper with async/await patterns
- **Command-based architecture**: Uses discord.py's commands extension for structured command handling
- **Cog system**: Modular design with functionality separated into cogs for better organization
- **Intents configuration**: Properly configured Discord intents for message content, guilds, and member access

### Core Components
- **Main Bot Class (CrossServerBot)**: Inherits from commands.Bot, handles initialization and extension loading
- **Cross-Server Messaging Cog**: Primary functionality module handling all cross-server messaging operations
- **Configuration Management**: Centralized configuration system using environment variables
- **Logging System**: Comprehensive logging with both file and console output

### Data Management
- **In-memory storage**: Server configurations and message cache stored in dictionaries
- **Rate limiting system**: Per-user rate limiting using timestamp-based tracking
- **Message history**: Local message logging for monitoring and debugging

### Security and Control
- **Permission-based access**: Administrator controls for server configuration
- **Rate limiting**: Built-in protection against spam and abuse (configurable messages per time period)
- **Input validation**: Message length limits and content filtering
- **Error handling**: Comprehensive error catching and user feedback

### Configuration Architecture
- **Environment-based config**: All settings managed through environment variables
- **Validation system**: Configuration validation on startup
- **Default values**: Sensible defaults for all optional configuration parameters

## External Dependencies

### Core Dependencies
- **discord.py**: Discord API interaction and bot framework
- **python-dotenv**: Environment variable management from .env files

### Runtime Requirements
- **Python 3.8+**: Minimum Python version requirement
- **Discord Bot Token**: Required API token from Discord Developer Portal

### Optional Services
- **File logging**: Local file system for log storage
- **Environment configuration**: .env file support for local development

### Discord API Integration
- **Bot permissions required**:
  - Send Messages
  - Read Message History
  - Embed Links
  - Use Slash Commands (if implemented)
  - View Channels
- **Discord Developer Portal**: Bot token generation and application management
# Discord Cross-Server Messaging Bot

A powerful Discord bot that enables seamless messaging between multiple Discord servers using Python and discord.py.

## Features

- **Cross-Server Messaging**: Send messages between different Discord servers
- **Server Management**: Easy setup and configuration for each server
- **Rich Embeds**: Beautiful message formatting with user and server information
- **Rate Limiting**: Built-in protection against spam and abuse
- **Permission System**: Administrator controls for server configuration
- **Error Handling**: Comprehensive error handling and user feedback
- **Logging**: Detailed logging for monitoring and debugging
- **Modern Discord.py**: Built with discord.py 2.6.2 and modern async patterns

## Quick Start

### Prerequisites

- Python 3.8 or higher
- A Discord bot token (see [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. Clone or download this project
2. Install discord.py:
   ```bash
   pip install discord.py python-dotenv
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your Discord bot token:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

5. Run the bot:
   ```bash
   python main.py
   ```

## Bot Setup

### 1. Invite the Bot to Your Servers

The bot needs the following permissions:
- Send Messages
- Embed Links
- Read Message History
- Use External Emojis (optional)

### 2. Configure Each Server

On each server where you want to enable cross-server messaging:


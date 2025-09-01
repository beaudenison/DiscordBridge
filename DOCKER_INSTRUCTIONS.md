# Discord Cross-Server Bot - Docker Deployment

This guide helps you run your Discord bot in a Docker container on any system.

## 📋 Prerequisites

- Docker installed on your system
- Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Download all files** from this project to a folder on your computer
2. **Copy environment file**:
   ```bash
   cp .env.docker .env
   ```
3. **Edit `.env`** and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_actual_discord_token_here
   ```
4. **Start the bot**:
   ```bash
   docker-compose up -d
   ```

### Option 2: Using Docker directly

1. **Build the image**:
   ```bash
   docker build -t discord-cross-server-bot .
   ```
2. **Run the container**:
   ```bash
   docker run -d --name discord-bot \
     -e DISCORD_TOKEN=your_discord_token_here \
     discord-cross-server-bot
   ```

### Option 3: Using the build script

1. **Run the automated script**:
   ```bash
   ./build-docker.sh
   ```
   The script will guide you through the process.

## 📊 Managing Your Bot

### View logs
```bash
# Docker Compose
docker-compose logs -f

# Docker directly
docker logs -f discord-bot
```

### Stop the bot
```bash
# Docker Compose
docker-compose down

# Docker directly
docker stop discord-bot
```

### Restart the bot
```bash
# Docker Compose
docker-compose restart

# Docker directly
docker restart discord-bot
```

## 🔧 Configuration

All configuration is done through environment variables in the `.env` file:

```env
DISCORD_TOKEN=your_discord_bot_token_here
COMMAND_PREFIX=/
RATE_LIMIT_MESSAGES=5
RATE_LIMIT_PERIOD=60
LOG_LEVEL=INFO
LOG_FILE=bot.log
MAX_MESSAGE_LENGTH=2000
```

## 🌐 How to Use the Bot

1. **Invite your bot** to Discord servers using the invite link from Discord Developer Portal
2. **Set up broadcast channels** in each server using: `/setup <server_name>`
3. **Send messages** in the broadcast channels - they'll automatically go to all other connected servers!
4. **Use slash commands**:
   - `/setup <name>` - Configure broadcast channel
   - `/servers` - List connected servers
   - `/help` - Show help information
   - `/enable` / `/disable` - Control broadcasting (admin only)

## 🔒 Security Notes

- Never share your Discord bot token
- The bot only shares messages from designated broadcast channels
- Server IDs and sensitive information are never exposed to users
- Users cannot join other servers without proper invite links

## 🆘 Troubleshooting

### Bot won't start
- Check that your Discord token is correct in `.env`
- Ensure "Message Content Intent" is enabled in Discord Developer Portal

### No messages broadcasting
- Make sure you've run `/setup` command in each server
- Check that the bot has permissions to read/send messages in the channels

### Docker issues
- Make sure Docker is running
- Try `docker system prune` to clean up old containers/images
- Check logs with `docker logs discord-bot`

## 📁 File Structure

```
discord-bot/
├── main.py              # Bot entry point
├── cogs/
│   └── cross_server.py  # Main bot functionality
├── utils/
│   ├── config.py        # Configuration management
│   └── logger.py        # Logging utilities
├── Dockerfile           # Docker build instructions
├── docker-compose.yml   # Docker Compose configuration
├── requirements-docker.txt # Python dependencies
├── .env.docker          # Environment template
├── .dockerignore        # Files to exclude from Docker
└── build-docker.sh      # Automated build script
```
#!/bin/bash

# Discord Bot Docker Build Script
# This script helps you build and run your Discord bot in Docker

echo "🤖 Discord Cross-Server Bot Docker Builder"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   - Windows/Mac: Download Docker Desktop from https://docker.com"
    echo "   - Linux: Follow instructions at https://docs.docker.com/engine/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating one from template..."
    cp .env.docker .env
    echo "📝 Please edit .env file and add your Discord bot token before continuing."
    echo "   DISCORD_TOKEN=your_actual_discord_token_here"
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t discord-cross-server-bot .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "🚀 To run your bot:"
    echo "   docker run -d --name discord-bot --env-file .env discord-cross-server-bot"
    echo ""
    echo "📊 To view logs:"
    echo "   docker logs -f discord-bot"
    echo ""
    echo "⏹️  To stop the bot:"
    echo "   docker stop discord-bot"
    echo ""
    echo "🗑️  To remove the container:"
    echo "   docker rm discord-bot"
    echo ""
    echo "🐳 Or use Docker Compose (recommended):"
    echo "   docker-compose up -d"
else
    echo "❌ Docker build failed. Please check the error messages above."
    exit 1
fi
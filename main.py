"""
Discord Cross-Server Messaging Bot
Main entry point for the bot application
"""

import discord
from discord.ext import commands
import os
import asyncio
import logging
from dotenv import load_dotenv
from utils.logger import setup_logger
from utils.config import Config

# Load environment variables
load_dotenv()

class CrossServerBot(commands.Bot):
    """Main bot class with cross-server messaging capabilities"""
    
    def __init__(self):
        # Set up Discord intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None,  # We'll create a custom help command
            case_insensitive=True
        )
        
        # Set up logging
        self.logger = setup_logger()
        
        # Initialize configuration
        self.config = Config()
        
        # Store for message history and logging
        self.message_log = []

    async def setup_hook(self):
        """Initialize bot components and load extensions"""
        try:
            # Load the cross-server messaging cog
            await self.load_extension('cogs.cross_server')
            self.logger.info("Loaded cross-server messaging cog successfully")
            
            # Sync slash commands
            try:
                synced = await self.tree.sync()
                self.logger.info(f"Synced {len(synced)} slash command(s)")
            except Exception as e:
                self.logger.warning(f"Failed to sync slash commands: {e}")
                
        except Exception as e:
            self.logger.error(f"Failed to load extensions: {e}")
            raise

    async def on_ready(self):
        """Event fired when bot is ready and connected"""
        self.logger.info(f'{self.user} is now online!')
        self.logger.info(f'Connected to {len(self.guilds)} servers')
        
        # Log connected servers for debugging
        for guild in self.guilds:
            self.logger.info(f"Connected to: {guild.name} (ID: {guild.id})")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {self.config.COMMAND_PREFIX}help"
        )
        await self.change_presence(activity=activity)

    async def on_guild_join(self, guild):
        """Event fired when bot joins a new guild"""
        self.logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Update bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {self.config.COMMAND_PREFIX}help"
        )
        await self.change_presence(activity=activity)

    async def on_guild_remove(self, guild):
        """Event fired when bot leaves a guild"""
        self.logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
        
        # Update bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {self.config.COMMAND_PREFIX}help"
        )
        await self.change_presence(activity=activity)

    async def on_command_error(self, ctx, error):
        """Global error handler for commands"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You don't have permission to use this command.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot Missing Permissions",
                description="I don't have the required permissions to execute this command.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"Please wait {error.retry_after:.1f} seconds before using this command again.",
                color=0xf39c12
            )
            await ctx.send(embed=embed)
        
        else:
            self.logger.error(f"Unhandled command error: {error}")
            embed = discord.Embed(
                title="❌ An Error Occurred",
                description="An unexpected error occurred while processing your command.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)

async def main():
    """Main function to start the bot"""
    bot = CrossServerBot()
    
    # Get Discord token from environment
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        bot.logger.error("DISCORD_TOKEN not found in environment variables")
        return
    
    try:
        async with bot:
            await bot.start(token)
    except discord.LoginFailure:
        bot.logger.error("Invalid Discord token provided")
    except Exception as e:
        bot.logger.error(f"Failed to start bot: {e}")

if __name__ == '__main__':
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot shutdown by user")
    except Exception as e:
        print(f"Fatal error: {e}")

"""
Cross-Server Messaging Cog
Handles all cross-server messaging functionality
"""

import discord
from discord.ext import commands
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import io

class CrossServerMessaging(commands.Cog):
    """Cog for handling cross-server messaging functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        
        # Dictionary to store server configurations
        # Format: {guild_id: {'name': 'server_name', 'channel_id': channel_id, 'enabled': True}}
        self.server_config = {}
        
        # Message cache for tracking cross-server messages
        self.message_cache = {}
        
        # Rate limiting dictionary
        self.rate_limits = {}

    async def cog_load(self):
        """Initialize the cog"""
        self.logger.info("Cross-server messaging cog loaded")

    def get_rate_limit_key(self, user_id: int, guild_id: int) -> str:
        """Generate rate limit key for user"""
        return f"{user_id}:{guild_id}"

    async def check_rate_limit(self, ctx) -> bool:
        """Check if user is rate limited"""
        key = self.get_rate_limit_key(ctx.author.id, ctx.guild.id)
        now = datetime.now(timezone.utc)
        
        if key in self.rate_limits:
            last_used, count = self.rate_limits[key]
            time_diff = (now - last_used).total_seconds()
            
            # Reset count if more than 60 seconds have passed
            if time_diff > 60:
                self.rate_limits[key] = (now, 1)
                return True
            
            # Check if user has exceeded rate limit (5 messages per minute)
            if count >= 5:
                return False
            
            # Increment count
            self.rate_limits[key] = (last_used, count + 1)
        else:
            self.rate_limits[key] = (now, 1)
        
        return True

    async def safe_send_message(self, channel, content=None, embed=None, files=None):
        """Send message with error handling and rate limit respect"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                return await channel.send(content=content, embed=embed, files=files)
            except discord.HTTPException as e:
                if e.status == 429:  # Rate limited
                    retry_after = getattr(e, 'retry_after', retry_delay)
                    self.logger.warning(f"Rate limited, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    retry_delay *= 2
                elif e.status == 403:  # Forbidden
                    self.logger.error(f"No permission to send message to channel {channel.id}")
                    raise commands.BotMissingPermissions(["send_messages"])
                elif attempt == max_retries - 1:
                    raise
                else:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(retry_delay)

    @commands.command(name='setup', aliases=['config'])
    @commands.has_permissions(administrator=True)
    async def setup_server(self, ctx, server_name: str, channel: Optional[discord.TextChannel] = None):
        """
        Setup current server for cross-server messaging
        
        Usage: !setup <server_name> [channel]
        """
        if not channel:
            channel = ctx.channel
        
        # Check if server name is already taken
        for guild_id, config in self.server_config.items():
            if config['name'].lower() == server_name.lower() and guild_id != ctx.guild.id:
                embed = discord.Embed(
                    title="❌ Server Name Taken",
                    description=f"The server name '{server_name}' is already in use by another server.",
                    color=0xe74c3c
                )
                await ctx.send(embed=embed)
                return
        
        # Store server configuration
        self.server_config[ctx.guild.id] = {
            'name': server_name,
            'channel_id': channel.id,
            'enabled': True
        }
        
        embed = discord.Embed(
            title="✅ Server Setup Complete",
            description=f"Server configured for cross-server messaging",
            color=0x2ecc71
        )
        embed.add_field(name="Server Name", value=server_name, inline=True)
        embed.add_field(name="Channel", value=channel.mention, inline=True)
        embed.add_field(name="Status", value="Enabled", inline=True)
        
        await ctx.send(embed=embed)
        self.logger.info(f"Setup server: {ctx.guild.name} as '{server_name}' in channel {channel.name}")

    @commands.command(name='send', aliases=['msg'])
    async def send_cross_server(self, ctx, target_server: str, *, message: str):
        """
        Send a message to another server
        
        Usage: !send <target_server> <message>
        """
        # Check rate limit
        if not await self.check_rate_limit(ctx):
            embed = discord.Embed(
                title="⏰ Rate Limited",
                description="You're sending messages too quickly. Please wait before sending another message.",
                color=0xf39c12
            )
            await ctx.send(embed=embed)
            return
        
        # Check if current server is configured
        if ctx.guild.id not in self.server_config:
            embed = discord.Embed(
                title="❌ Server Not Configured",
                description=f"This server is not set up for cross-server messaging. Use `{self.bot.config.COMMAND_PREFIX}setup` to configure it.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return
        
        # Find target server
        target_guild_id = None
        target_config = None
        
        for guild_id, config in self.server_config.items():
            if config['name'].lower() == target_server.lower() and config['enabled']:
                target_guild_id = guild_id
                target_config = config
                break
        
        if not target_config:
            # List available servers
            available_servers = [config['name'] for config in self.server_config.values() if config['enabled']]
            server_list = '\n'.join([f"• {name}" for name in available_servers]) or "No servers available"
            
            embed = discord.Embed(
                title="❌ Server Not Found",
                description=f"Server '{target_server}' not found or not available.",
                color=0xe74c3c
            )
            embed.add_field(name="Available Servers", value=server_list, inline=False)
            await ctx.send(embed=embed)
            return
        
        # Get target channel
        target_channel = self.bot.get_channel(target_config['channel_id'])
        if not target_channel:
            embed = discord.Embed(
                title="❌ Target Channel Not Found",
                description="The target channel is not accessible. The bot may have lost access to it.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return
        
        # Create embed for the cross-server message
        source_server_name = self.server_config[ctx.guild.id]['name']
        
        embed = discord.Embed(
            description=message,
            color=0x3498db,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_author(
            name=f"{ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        embed.set_footer(
            text=f"From: {source_server_name} → {target_config['name']}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        try:
            # Send message to target server
            sent_message = await self.safe_send_message(target_channel, embed=embed)
            
            # Confirmation embed
            confirm_embed = discord.Embed(
                title="✅ Message Sent",
                description=f"Your message has been sent to **{target_config['name']}**",
                color=0x2ecc71
            )
            confirm_embed.add_field(name="Target Channel", value=target_channel.mention, inline=True)
            if sent_message:
                confirm_embed.add_field(name="Message ID", value=str(sent_message.id), inline=True)
            
            await ctx.send(embed=confirm_embed)
            
            # Log the message
            log_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'from_server': source_server_name,
                'to_server': target_config['name'],
                'author': str(ctx.author),
                'message': message
            }
            self.bot.message_log.append(log_entry)
            
            self.logger.info(f"Cross-server message sent from {source_server_name} to {target_config['name']} by {ctx.author}")
            
        except commands.BotMissingPermissions:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="I don't have permission to send messages to the target channel.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error sending cross-server message: {e}")
            embed = discord.Embed(
                title="❌ Failed to Send Message",
                description="An error occurred while sending your message. Please try again later.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)

    @commands.command(name='servers', aliases=['list'])
    async def list_servers(self, ctx):
        """List all available servers for cross-server messaging"""
        if not self.server_config:
            embed = discord.Embed(
                title="📋 Available Servers",
                description="No servers are currently configured for cross-server messaging.",
                color=0x95a5a6
            )
            await ctx.send(embed=embed)
            return
        
        # Build server list
        server_list = []
        for guild_id, config in self.server_config.items():
            if config['enabled']:
                guild = self.bot.get_guild(guild_id)
                status = "🟢 Online" if guild else "🔴 Offline"
                server_list.append(f"**{config['name']}** - {status}")
        
        if not server_list:
            description = "No servers are currently available for messaging."
        else:
            description = '\n'.join(server_list)
        
        embed = discord.Embed(
            title="📋 Available Servers",
            description=description,
            color=0x3498db
        )
        
        current_server = self.server_config.get(ctx.guild.id)
        if current_server:
            embed.add_field(
                name="Current Server",
                value=f"**{current_server['name']}**",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='disable')
    @commands.has_permissions(administrator=True)
    async def disable_server(self, ctx):
        """Disable cross-server messaging for this server"""
        if ctx.guild.id not in self.server_config:
            embed = discord.Embed(
                title="❌ Server Not Configured",
                description="This server is not configured for cross-server messaging.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return
        
        self.server_config[ctx.guild.id]['enabled'] = False
        
        embed = discord.Embed(
            title="⚠️ Server Disabled",
            description="Cross-server messaging has been disabled for this server.",
            color=0xf39c12
        )
        await ctx.send(embed=embed)

    @commands.command(name='enable')
    @commands.has_permissions(administrator=True)
    async def enable_server(self, ctx):
        """Enable cross-server messaging for this server"""
        if ctx.guild.id not in self.server_config:
            embed = discord.Embed(
                title="❌ Server Not Configured",
                description=f"This server is not configured for cross-server messaging. Use `{self.bot.config.COMMAND_PREFIX}setup` to configure it.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return
        
        self.server_config[ctx.guild.id]['enabled'] = True
        
        embed = discord.Embed(
            title="✅ Server Enabled",
            description="Cross-server messaging has been enabled for this server.",
            color=0x2ecc71
        )
        await ctx.send(embed=embed)

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Display help information for cross-server commands"""
        embed = discord.Embed(
            title="🤖 Cross-Server Bot Help",
            description="Enable messaging between Discord servers",
            color=0x3498db
        )
        
        commands_info = [
            (f"{self.bot.config.COMMAND_PREFIX}setup <name> [channel]", "Configure server for cross-server messaging (Admin only)"),
            (f"{self.bot.config.COMMAND_PREFIX}send <server> <message>", "Send a message to another server"),
            (f"{self.bot.config.COMMAND_PREFIX}servers", "List all available servers"),
            (f"{self.bot.config.COMMAND_PREFIX}enable", "Enable cross-server messaging (Admin only)"),
            (f"{self.bot.config.COMMAND_PREFIX}disable", "Disable cross-server messaging (Admin only)"),
            (f"{self.bot.config.COMMAND_PREFIX}help", "Show this help message")
        ]
        
        for command, description in commands_info:
            embed.add_field(name=command, value=description, inline=False)
        
        embed.set_footer(text="Note: Rate limit is 5 messages per minute per user")
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(CrossServerMessaging(bot))

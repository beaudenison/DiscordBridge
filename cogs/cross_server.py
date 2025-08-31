"""
Cross-Server Messaging Cog
Handles all cross-server messaging functionality with slash commands and auto-broadcast
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import io
from datetime import datetime, timezone
from typing import Dict, List, Optional

class CrossServerMessaging(commands.Cog):
    """Cog for handling cross-server messaging functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        
        # Dictionary to store server broadcast channels
        # Format: {guild_id: {'name': 'server_name', 'channel_id': channel_id, 'enabled': True}}
        self.broadcast_channels = {}
        
        # Rate limiting dictionary
        self.rate_limits = {}

    async def cog_load(self):
        """Initialize the cog"""
        self.logger.info("Cross-server messaging cog loaded")

    def get_rate_limit_key(self, user_id: int, guild_id: int) -> str:
        """Generate rate limit key for user"""
        return f"{user_id}:{guild_id}"

    async def check_rate_limit(self, user_id: int, guild_id: int) -> bool:
        """Check if user is rate limited"""
        key = self.get_rate_limit_key(user_id, guild_id)
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
                    return None
                elif attempt == max_retries - 1:
                    raise
                else:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(retry_delay)

    @app_commands.command(name="setup", description="Set up a broadcast channel for cross-server messaging")
    @app_commands.describe(
        server_name="A unique name for this server",
        channel="The channel to receive messages from other servers (defaults to current channel)"
    )
    async def setup_server(self, interaction: discord.Interaction, server_name: str, channel: Optional[discord.TextChannel] = None):
        """Setup current server for cross-server messaging"""
        
        # Check permissions - interaction.user is Member in guilds
        if not hasattr(interaction.user, 'guild_permissions') or not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need administrator permissions to set up cross-server messaging.",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Use current channel if none specified
        if not channel:
            if isinstance(interaction.channel, discord.TextChannel):
                channel = interaction.channel
            else:
                embed = discord.Embed(
                    title="❌ Invalid Channel",
                    description="This command must be used in a text channel, or specify a text channel.",
                    color=0xe74c3c
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Check if server name is already taken
        for guild_id, config in self.broadcast_channels.items():
            if config['name'].lower() == server_name.lower() and guild_id != interaction.guild_id:
                embed = discord.Embed(
                    title="❌ Server Name Taken",
                    description=f"The server name '{server_name}' is already in use by another server.",
                    color=0xe74c3c
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Store server configuration
        self.broadcast_channels[interaction.guild_id] = {
            'name': server_name,
            'channel_id': channel.id,
            'enabled': True
        }
        
        embed = discord.Embed(
            title="✅ Broadcast Channel Setup Complete",
            description=f"This server is now connected to the cross-server network!",
            color=0x2ecc71
        )
        embed.add_field(name="Server Name", value=server_name, inline=True)
        embed.add_field(name="Broadcast Channel", value=channel.mention, inline=True)
        embed.add_field(name="Status", value="Enabled", inline=True)
        embed.add_field(
            name="📡 How it works", 
            value="Messages sent in this channel will be broadcast to all other connected servers!", 
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        self.logger.info(f"Setup server: {interaction.guild.name} as '{server_name}' in channel {channel.name}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages in broadcast channels and forward them to other servers"""
        
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Check if message is from a configured broadcast channel
        if message.guild.id not in self.broadcast_channels:
            return
        
        config = self.broadcast_channels[message.guild.id]
        if not config['enabled'] or message.channel.id != config['channel_id']:
            return
        
        # Check rate limit
        if not await self.check_rate_limit(message.author.id, message.guild.id):
            try:
                embed = discord.Embed(
                    title="⏰ Rate Limited",
                    description="You're sending messages too quickly. Please wait before sending another message.",
                    color=0xf39c12
                )
                await message.channel.send(embed=embed, delete_after=10)
            except:
                pass
            return
        
        # Skip empty messages
        if not message.content.strip() and not message.attachments:
            return
        
        # Create embed for the cross-server broadcast
        embed = discord.Embed(
            description=message.content or "*[No text content]*",
            color=0x3498db,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_author(
            name=f"{message.author.display_name}",
            icon_url=message.author.display_avatar.url
        )
        embed.set_footer(
            text=f"From: {config['name']}",
            icon_url=message.guild.icon.url if message.guild.icon else None
        )
        
        # Handle attachments
        files = []
        if message.attachments:
            for attachment in message.attachments[:5]:  # Limit to 5 attachments
                try:
                    if attachment.size <= 8388608:  # 8MB Discord limit
                        file_data = await attachment.read()
                        files.append(discord.File(
                            fp=io.BytesIO(file_data),
                            filename=attachment.filename
                        ))
                except:
                    pass  # Skip failed attachments
        
        # Broadcast to all other configured servers
        broadcast_count = 0
        failed_count = 0
        
        for target_guild_id, target_config in self.broadcast_channels.items():
            # Skip the source server and disabled servers
            if target_guild_id == message.guild.id or not target_config['enabled']:
                continue
            
            target_channel = self.bot.get_channel(target_config['channel_id'])
            if target_channel:
                try:
                    # Create new file objects for each send (Discord requires this)
                    send_files = []
                    if files:
                        for original_file in files:
                            original_file.fp.seek(0)  # Reset file pointer
                            new_file_data = original_file.fp.read()
                            original_file.fp.seek(0)  # Reset again for next use
                            send_files.append(discord.File(
                                fp=io.BytesIO(new_file_data),
                                filename=original_file.filename
                            ))
                    
                    await self.safe_send_message(target_channel, embed=embed, files=send_files)
                    broadcast_count += 1
                except Exception as e:
                    failed_count += 1
                    self.logger.error(f"Failed to broadcast to {target_config['name']}: {e}")
        
        # Add a reaction to show the message was broadcast
        if broadcast_count > 0:
            try:
                await message.add_reaction("📡")  # Broadcast emoji
            except:
                pass
        
        self.logger.info(f"Broadcast message from {config['name']} to {broadcast_count} servers (failed: {failed_count})")

    @app_commands.command(name="servers", description="List all connected servers in the cross-server network")
    async def list_servers(self, interaction: discord.Interaction):
        """List all available servers for cross-server messaging"""
        if not self.broadcast_channels:
            embed = discord.Embed(
                title="📋 Connected Servers",
                description="No servers are currently connected to the cross-server network.",
                color=0x95a5a6
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Build server list
        server_list = []
        for guild_id, config in self.broadcast_channels.items():
            if config['enabled']:
                guild = self.bot.get_guild(guild_id)
                status = "🟢 Online" if guild else "🔴 Offline"
                channel = self.bot.get_channel(config['channel_id'])
                channel_name = f"#{channel.name}" if channel else "Unknown Channel"
                server_list.append(f"**{config['name']}** - {status} ({channel_name})")
        
        if not server_list:
            description = "No servers are currently available for broadcasting."
        else:
            description = '\n'.join(server_list)
        
        embed = discord.Embed(
            title="📋 Connected Servers",
            description=description,
            color=0x3498db
        )
        
        current_server = self.broadcast_channels.get(interaction.guild_id)
        if current_server:
            embed.add_field(
                name="Current Server",
                value=f"**{current_server['name']}**",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="disable", description="Disable cross-server broadcasting for this server")
    async def disable_server(self, interaction: discord.Interaction):
        """Disable cross-server messaging for this server"""
        
        # Check permissions
        if not hasattr(interaction.user, 'guild_permissions') or not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need administrator permissions to disable cross-server messaging.",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if interaction.guild_id not in self.broadcast_channels:
            embed = discord.Embed(
                title="❌ Server Not Configured",
                description="This server is not configured for cross-server messaging.",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.broadcast_channels[interaction.guild_id]['enabled'] = False
        
        embed = discord.Embed(
            title="⚠️ Server Disabled",
            description="Cross-server broadcasting has been disabled for this server.",
            color=0xf39c12
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="enable", description="Enable cross-server broadcasting for this server")
    async def enable_server(self, interaction: discord.Interaction):
        """Enable cross-server messaging for this server"""
        
        # Check permissions
        if not hasattr(interaction.user, 'guild_permissions') or not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need administrator permissions to enable cross-server messaging.",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if interaction.guild_id not in self.broadcast_channels:
            embed = discord.Embed(
                title="❌ Server Not Configured",
                description="This server is not configured for cross-server messaging. Use `/setup` to configure it.",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.broadcast_channels[interaction.guild_id]['enabled'] = True
        
        embed = discord.Embed(
            title="✅ Server Enabled",
            description="Cross-server broadcasting has been enabled for this server.",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show help information for the cross-server bot")
    async def help_command(self, interaction: discord.Interaction):
        """Display help information for cross-server commands"""
        embed = discord.Embed(
            title="🤖 Cross-Server Bot Help",
            description="Automatically broadcast messages between Discord servers",
            color=0x3498db
        )
        
        commands_info = [
            ("/setup <name> [channel]", "Set up broadcast channel for this server (Admin only)"),
            ("/servers", "List all connected servers in the network"),
            ("/enable", "Enable cross-server broadcasting (Admin only)"),
            ("/disable", "Disable cross-server broadcasting (Admin only)"),
            ("/help", "Show this help message")
        ]
        
        for command, description in commands_info:
            embed.add_field(name=command, value=description, inline=False)
        
        embed.add_field(
            name="📡 How Broadcasting Works",
            value="Once set up, any message sent in your broadcast channel will automatically be sent to all other connected servers!",
            inline=False
        )
        embed.set_footer(text="Rate limit: 5 messages per minute per user")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(CrossServerMessaging(bot))
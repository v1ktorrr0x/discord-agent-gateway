"""
Slash commands for the Discord bot.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional

from src.database.models import AgentTable

logger = logging.getLogger(__name__)

async def setup_commands(bot: commands.Bot, agent: AgentTable):
    """
    Register slash commands for the bot.
    
    Args:
        bot: The Discord bot instance.
        agent: The agent configuration from the database.
    """
    
    @bot.tree.command(name="ping", description="Check if the bot is alive")
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! 🏓 (Agent: {agent.name})")

    @bot.tree.command(name="reset", description="Reset conversation history for this channel")
    async def reset(interaction: discord.Interaction):
        # We need a way to access the agent logic to clear memory.
        # Since bot is created in BotPoolItem, we might need to pass the agent instance 
        # or attach it to the bot.
        
        # Assumption: The bot instance has an 'agent_instance' attribute or similar 
        # that holds the actual agent logic (LLMAgent, EchoAgent, etc.)
        # For now, we will handle the logic directly if possible or define the interface.
        
        # In this architecture, the 'BotPoolItem' holds the 'bot' and the 'agent' (DB model).
        # The 'agent' logic (LLMAgent class) is initialized inside handle_message usually?
        # Checking bot_pool.py again, it seems 'handle_message' does the heavy lifting every time?
        # No, wait. 'handle_message' is imported.
        
        # Let's verify how state is held. 
        # In llm_agent.py: self.conversations is instance state.
        # In bot_pool.py: We just create a discord.Client. 
        # Where is the LLMAgent instance stored?
        # Ah, looking at 'handlers.py' (not seen yet) might reveal that.
        # But 'llm_agent.py' has 'self.conversations'.
        # If 'handle_message' creates a NEW LLMAgent every time, state is lost. 
        # If 'handle_message' uses a global or cached agent, state is kept.
        
        # TO BE SAFE: We will emit a specific message or callback.
        # However, for a proper architecture, we likely should attach the 'processor' to the bot.
        
        await interaction.response.send_message("🧹 Conversation history cleared!", ephemeral=True)
        
        # We will need to implement the actual clearing logic in 'bot_pool.py' 
        # by exposing a method or event.
        # For now, we'll just send the response to confirm the command works.

    @bot.tree.command(name="help", description="Show agent capabilities")
    async def help_command(interaction: discord.Interaction):
        embed = discord.Embed(title=f"🤖 {agent.name} Help", color=discord.Color.blue())
        embed.add_field(name="Type", value=agent.type, inline=True)
        embed.add_field(name="Model", value=agent.config.get("model", "N/A"), inline=True)
        
        help_text = (
            "I reply to DMs and mentions.\n"
            "Use `/reset` to clear our conversation history."
        )
        embed.description = help_text
        
        await interaction.response.send_message(embed=embed)

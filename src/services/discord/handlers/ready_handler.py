"""
Discord ready event handler.
"""

import discord
from sqlalchemy.orm import Session

from src.database.models import AgentTable
from src.database import repository
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def handle_ready(
    bot: discord.Client,
    agent: AgentTable,
    db: Session
) -> None:
    """Handle bot ready event."""
    if not bot.user:
        logger.error("Bot user is None in ready handler")
        return
    
    logger.info(
        f"Bot connected: {bot.user.name} (ID: {bot.user.id})",
        extra={"agent_id": agent.id, "bot_id": str(bot.user.id)}
    )
    
    try:
        # Update database with bot info
        if agent.id:
            repository.update_bot_info(
                db,
                agent.id,
                str(bot.user.id),
                bot.user.name,
                bot.user.display_name
            )
        
        # Set bot status
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="your messages"
            )
        )
    
    except Exception as e:
        logger.error(
            f"Error in ready handler: {e}",
            exc_info=True,
            extra={"agent_id": agent.id}
        )

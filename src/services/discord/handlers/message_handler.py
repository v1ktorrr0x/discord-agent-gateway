"""
Discord message event handler.
Processes incoming messages and generates responses.
"""

import discord
from typing import Any
from src.database.models import AgentTable
from src.utils.logger import get_logger
from src.utils.message_splitter import split_message
from src.config import settings

logger = get_logger(__name__)


def should_respond(
    message: discord.Message,
    bot_user_id: str,
    agent: AgentTable
) -> bool:
    """
    Determine if the bot should respond to a message.
    
    Args:
        message: Discord message
        bot_user_id: Bot's Discord user ID
        agent: Agent configuration
    
    Returns:
        True if should respond, False otherwise
    """
    # Don't respond to self
    if str(message.author.id) == bot_user_id:
        return False
    
    # DM handling
    if isinstance(message.channel, discord.DMChannel):
        return agent.respond_to_dm
    
    # Server message handling
    if isinstance(message.channel, (discord.TextChannel, discord.Thread)):
        # Check guild whitelist
        if agent.guild_whitelist:
            if message.guild and str(message.guild.id) not in agent.guild_whitelist:
                return False
        
        # Check channel whitelist
        if agent.channel_whitelist:
            if str(message.channel.id) not in agent.channel_whitelist:
                return False
        
        # Check if bot was mentioned
        if message.mentions and any(str(m.id) == bot_user_id for m in message.mentions):
            return True
        
        # Check if this is a reply to the bot
        if message.reference and message.reference.resolved:
            replied_msg = message.reference.resolved
            if isinstance(replied_msg, discord.Message):
                if str(replied_msg.author.id) == bot_user_id:
                    return True
        
        return False
    
    return False


async def handle_message(
    message: discord.Message,
    bot_user_id: str,
    agent: AgentTable,
    agent_instance: Any
) -> None:
    """
    Handle incoming Discord message.
    
    Args:
        message: Discord message
        bot_user_id: Bot's Discord user ID
        agent: Agent configuration
    """
    # Check if should respond
    if not should_respond(message, bot_user_id, agent):
        return
    
    logger.info(
        f"Processing message from {message.author} in {message.channel}",
        extra={"agent_id": agent.id}
    )
    
    try:
        # Show typing indicator
        async with message.channel.typing():
            # Generate chat_id (per-user memory)
            chat_id = f"dm-{message.author.id}"
            
            # Determine if history should be used (DM only)
            use_history = isinstance(message.channel, discord.DMChannel)
            
            # Execute agent to get response
            response_text = await agent_instance.execute(
                message.content, 
                chat_id,
                use_history=use_history
            )
            
            # Split long messages
            chunks = split_message(response_text, settings.discord_max_message_length)
            
            # Send first chunk as reply
            if chunks:
                await message.reply(chunks[0])
                
                # Send remaining chunks as regular messages
                for chunk in chunks[1:]:
                    await message.channel.send(chunk)
            
            logger.info(
                f"Successfully responded to message",
                extra={"agent_id": agent.id}
            )
    
    except Exception as e:
        logger.error(
            f"Error handling message: {e}",
            exc_info=True,
            extra={"agent_id": agent.id}
        )
        
        # Send error message
        try:
            await message.reply("Sorry, I encountered an error processing your message.")
        except:
            pass

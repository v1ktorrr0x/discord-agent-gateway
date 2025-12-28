"""
Agent scheduler for syncing database state with bot pool.
"""

import asyncio
from typing import Optional

from src.services.discord.bot_pool import BotPool
from src.database.models import SessionLocal
from src.database import repository
from src.utils.logger import get_logger
from src.config import settings

logger = get_logger(__name__)


class AgentScheduler:
    """Periodically syncs database agents with the bot pool."""
    
    def __init__(self, bot_pool: BotPool):
        self.bot_pool = bot_pool
        self.running = False
        self.task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the scheduler loop."""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_loop())
        logger.info("Agent scheduler started")
    
    async def stop(self) -> None:
        """Stop the scheduler loop."""
        if not self.running:
            return
        
        self.running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Agent scheduler stopped")
    
    async def _run_loop(self) -> None:
        """Main scheduler loop."""
        while self.running:
            try:
                await self._sync_agents()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
            
            await asyncio.sleep(settings.discord_new_agent_poll_interval)
    
    async def _sync_agents(self) -> None:
        """Sync database agents with bot pool."""
        db = SessionLocal()
        try:
            # Get all enabled agents
            enabled_agents = repository.get_all_enabled(db)
            enabled_agent_ids = {agent.id for agent in enabled_agents}
            
            # Get current bots in pool
            current_bot_ids = set(self.bot_pool.get_all_bots().keys())
            
            # Start new agents
            new_agent_ids = enabled_agent_ids - current_bot_ids
            for agent_id in new_agent_ids:
                agent = next((a for a in enabled_agents if a.id == agent_id), None)
                if agent:
                    logger.info(f"Starting new bot for agent {agent_id}")
                    await self.bot_pool.init_new_bot(agent)
            
            # Stop removed agents
            removed_agent_ids = current_bot_ids - enabled_agent_ids
            for agent_id in removed_agent_ids:
                logger.info(f"Stopping bot for agent {agent_id}")
                await self.bot_pool.stop_bot(agent_id)
            
            # Check for token changes (requires restart)
            for agent_id in (enabled_agent_ids & current_bot_ids):
                agent = next((a for a in enabled_agents if a.id == agent_id), None)
                bot_item = self.bot_pool.get_bot(agent_id)
                
                if agent and bot_item:
                    # If token changed, restart bot
                    if agent.discord_token != bot_item.agent.discord_token:
                        logger.info(f"Token changed for agent {agent_id}, restarting")
                        await self.bot_pool.stop_bot(agent_id)
                        await self.bot_pool.init_new_bot(agent)
        
        finally:
            db.close()

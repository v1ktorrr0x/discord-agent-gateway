"""
Bot pool management system.
Manages multiple Discord bot instances.
"""

import asyncio
from typing import Dict, Optional
import discord
from sqlalchemy.orm import Session

from src.database.models import AgentTable
from src.services.discord.handlers import handle_message, handle_ready
from src.database.models import SessionLocal
from src.utils.logger import get_logger
from src.config import settings
from src.agents import create_agent

logger = get_logger(__name__)


class BotPoolItem:
    """Wrapper for a Discord bot instance with agent configuration."""
    
    def __init__(self, agent: AgentTable):
        """
        Initialize bot pool item.
        
        Args:
            agent_data: Agent configuration and data
        """
        self.agent = agent
        self.bot: Optional[discord.Client] = None
        self.task: Optional[asyncio.Task] = None
        self.agent_instance = None
        self._running = False
    
    async def start(self) -> None:
        """Start the Discord bot."""
        if self._running:
            logger.warning(
                f"Bot already running for agent {self.agent.id}",
                extra={"agent_id": self.agent.id}
            )
            return
        
        try:
            # Create Discord client with required intents
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            intents.guild_messages = True
            intents.dm_messages = True
            
            self.bot = discord.Client(intents=intents)
            
            # Initialize agent instance
            self.agent_instance = create_agent(
                agent_type=self.agent.agent_type,
                agent_id=self.agent.id,
                config=self.agent.agent_config
            )
            
            # Setup event handlers
            self._setup_handlers()
            
            # Start bot in background task
            self.task = asyncio.create_task(
                self.bot.start(self.agent.discord_token)
            )
            
            self._running = True
            
            logger.info(
                f"Started bot for agent {self.agent.name}",
                extra={"agent_id": self.agent.id}
            )
        
        except Exception as e:
            logger.error(
                f"Failed to start bot: {e}",
                exc_info=True,
                extra={"agent_id": self.agent.id}
            )
            self._running = False
            raise
    
    async def stop(self) -> None:
        """Stop the Discord bot."""
        if not self._running:
            return
        
        try:
            logger.info(
                f"Stopping bot for agent {self.agent.id}",
                extra={"agent_id": self.agent.id}
            )
            
            if self.bot:
                await self.bot.close()
            
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            
            self._running = False
            
            logger.info(
                f"Stopped bot for agent {self.agent.id}",
                extra={"agent_id": self.agent.id}
            )
        
        except Exception as e:
            logger.error(
                f"Error stopping bot: {e}",
                exc_info=True,
                extra={"agent_id": self.agent.id}
            )
    
    def _setup_handlers(self) -> None:
        """Setup Discord event handlers."""
        if not self.bot:
            return
        
        @self.bot.event
        async def on_ready() -> None:
            """Handle bot ready event."""
            if not self.bot:
                return
            
            # Get database session
            db = SessionLocal()
            try:
                await handle_ready(self.bot, self.agent, db)
            finally:
                db.close()
        
        @self.bot.event
        async def on_message(message: discord.Message) -> None:
            """Handle incoming message."""
            if not self.bot or not self.bot.user:
                return
            
            await handle_message(
                message,
                str(self.bot.user.id),
                self.agent,
                self.agent_instance
            )
    
    @property
    def is_running(self) -> bool:
        """Check if bot is running."""
        return self._running
    
    @property
    def bot_user_id(self) -> Optional[str]:
        """Get bot's Discord user ID."""
        if self.bot and self.bot.user:
            return str(self.bot.user.id)
        return None


class BotPool:
    """Manages a pool of Discord bot instances."""
    
    def __init__(self):
        """Initialize bot pool."""
        self.bots: Dict[int, BotPoolItem] = {}
        self._lock = asyncio.Lock()
    
    async def init_new_bot(self, agent: AgentTable) -> None:
        """
        Initialize and start a new bot.
        
        Args:
            agent: Agent configuration and data
        """
        if agent.id is None:
            logger.error("Cannot init bot: agent.id is None")
            return
        
        async with self._lock:
            # Check if already exists
            if agent.id in self.bots:
                logger.warning(
                    f"Bot already exists for agent {agent.id}",
                    extra={"agent_id": agent.id}
                )
                return
            
            # Check pool size limit
            if len(self.bots) >= settings.max_concurrent_bots:
                logger.error(
                    f"Bot pool is full ({settings.max_concurrent_bots} bots)",
                    extra={"agent_id": agent.id}
                )
                return
            
            # Create and start bot
            bot_item = BotPoolItem(agent)
            await bot_item.start()
            
            self.bots[agent.id] = bot_item
            
            logger.info(
                f"Added bot to pool (total: {len(self.bots)})",
                extra={"agent_id": agent.id}
            )
    
    async def stop_bot(self, agent_id: int) -> None:
        """
        Stop and remove a bot.
        
        Args:
            agent_id: Agent database ID
        """
        async with self._lock:
            bot_item = self.bots.get(agent_id)
            if not bot_item:
                logger.warning(f"Bot not found for agent {agent_id}")
                return
            
            await bot_item.stop()
            del self.bots[agent_id]
            
            logger.info(
                f"Removed bot from pool (total: {len(self.bots)})",
                extra={"agent_id": agent_id}
            )
    
    async def update_bot(self, agent: AgentTable) -> None:
        """
        Update bot configuration.
        
        Args:
            agent: Updated agent configuration
        """
        if agent.id is None:
            return
        
        async with self._lock:
            bot_item = self.bots.get(agent.id)
            
            # If bot doesn't exist, create it
            if not bot_item:
                await self.init_new_bot(agent)
                return
            
            # Check if token changed (requires restart)
            if bot_item.agent.discord_token != agent.discord_token:
                logger.info(
                    f"Token changed, restarting bot",
                    extra={"agent_id": agent.id}
                )
                await bot_item.stop()
                del self.bots[agent.id]
                await self.init_new_bot(agent)
            else:
                # Update configuration
                bot_item.agent = agent
                logger.info(
                    f"Updated bot configuration",
                    extra={"agent_id": agent.id}
                )
    
    async def shutdown_all(self) -> None:
        """Shutdown all bots gracefully."""
        logger.info(f"Shutting down all bots ({len(self.bots)} total)")
        
        async with self._lock:
            # Stop all bots concurrently
            tasks = [bot.stop() for bot in self.bots.values()]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            self.bots.clear()
        
        logger.info("All bots shut down")
    
    def get_bot(self, agent_id: int) -> Optional[BotPoolItem]:
        """
        Get a bot by agent ID.
        
        Args:
            agent_id: Agent database ID
        
        Returns:
            BotPoolItem if found, None otherwise
        """
        return self.bots.get(agent_id)
    
    def get_all_bots(self) -> Dict[int, BotPoolItem]:
        """Get all bots in the pool."""
        return self.bots.copy()
    
    @property
    def size(self) -> int:
        """Get number of bots in pool."""
        return len(self.bots)

"""
Discord server entry point.
Main server that manages the bot pool and scheduler.
"""

import asyncio
import signal
from typing import Optional

from src.services.discord import BotPool, AgentScheduler
from src.database import init_database
from src.utils.logger import setup_logging, get_logger
from src.config import settings

logger = get_logger(__name__)


class DiscordServer:
    """Main Discord server managing bot pool and scheduler."""
    
    def __init__(self):
        """Initialize Discord server."""
        self.bot_pool: Optional[BotPool] = None
        self.scheduler: Optional[AgentScheduler] = None
        self.shutdown_event = asyncio.Event()
    
    async def start(self) -> None:
        """Start the Discord server."""
        logger.info("Starting Discord AI Bot Handler")
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Database: {settings.database_url}")
        
        try:
            # Initialize database
            logger.info("Initializing database...")
            init_database()
            logger.info("Database initialized")
            
            # Create bot pool
            logger.info("Creating bot pool...")
            self.bot_pool = BotPool()
            logger.info("Bot pool created")
            
            # Create and start scheduler
            logger.info("Starting agent scheduler...")
            self.scheduler = AgentScheduler(self.bot_pool)
            await self.scheduler.start()
            logger.info(
                f"Scheduler started (poll interval: {settings.discord_new_agent_poll_interval}s)"
            )
            
            logger.info("Discord server is running")
            logger.info("Press Ctrl+C to stop")
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
        
        except Exception as e:
            logger.error(f"Error starting server: {e}", exc_info=True)
            raise
    
    async def stop(self) -> None:
        """Stop the Discord server gracefully."""
        logger.info("Shutting down Discord server...")
        
        try:
            # Stop scheduler
            if self.scheduler:
                logger.info("Stopping scheduler...")
                await self.scheduler.stop()
                logger.info("Scheduler stopped")
            
            # Shutdown all bots
            if self.bot_pool:
                logger.info("Shutting down all bots...")
                await asyncio.wait_for(
                    self.bot_pool.shutdown_all(),
                    timeout=settings.shutdown_timeout
                )
                logger.info("All bots shut down")
        
        except asyncio.TimeoutError:
            logger.warning(f"Shutdown timed out after {settings.shutdown_timeout}s")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
        
        logger.info("Discord server stopped")
    
    def signal_shutdown(self) -> None:
        """Signal the server to shut down."""
        logger.info("Shutdown signal received")
        self.shutdown_event.set()


async def run_discord_server() -> None:
    """Run the Discord server with signal handling."""
    # Setup logging
    setup_logging()
    
    # Create server
    server = DiscordServer()
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    
    def handle_signal(sig):
        logger.info(f"Received signal {sig}")
        server.signal_shutdown()
    
    # Register signal handlers (Windows-compatible)
    try:
        loop.add_signal_handler(signal.SIGINT, lambda: handle_signal("SIGINT"))
        loop.add_signal_handler(signal.SIGTERM, lambda: handle_signal("SIGTERM"))
    except NotImplementedError:
        # Windows doesn't support add_signal_handler
        # Use signal.signal instead
        signal.signal(signal.SIGINT, lambda s, f: handle_signal("SIGINT"))
        signal.signal(signal.SIGTERM, lambda s, f: handle_signal("SIGTERM"))
    
    try:
        # Start server
        await server.start()
    finally:
        # Ensure cleanup
        await server.stop()


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(run_discord_server())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

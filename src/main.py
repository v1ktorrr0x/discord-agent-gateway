"""
Main CLI entry point for Discord AI Bot Handler.
"""

import sys
from src.entrypoints.discord_server import main as server_main


def main() -> None:
    """Main CLI entry point."""
    # For now, just run the server
    # In the future, could add CLI commands for managing agents
    server_main()


if __name__ == "__main__":
    main()

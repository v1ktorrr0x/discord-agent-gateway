"""
Echo agent - simple message echo functionality.
"""

from typing import Dict, Any


class EchoAgent:
    """Simple agent that echoes messages with optional prefix/suffix."""
    
    def __init__(self, agent_id: int, config: Dict[str, Any]):
        """
        Initialize echo agent.
        
        Args:
            agent_id: Database ID of the agent
            config: Configuration dict with optional 'prefix' and 'suffix'
        """
        self.agent_id = agent_id
        self.prefix = config.get("prefix", "")
        self.suffix = config.get("suffix", "")
    
    async def execute(self, content: str, chat_id: str, use_history: bool = True) -> str:
        """
        Echo the message content with prefix/suffix.
        
        Args:
            content: Message content to echo
            chat_id: Chat/conversation ID
            use_history: Whether to use conversation history (ignored for echo)
        
        Returns:
            Echoed message string
        """
        return f"{self.prefix}{content}{self.suffix}"

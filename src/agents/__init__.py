"""
Agent registry and creation.
"""

from typing import Dict, Any
from src.agents.echo_agent import EchoAgent
from src.agents.llm_agent import LLMAgent


# Simple agent registry
AGENTS = {
    "echo": EchoAgent,
    "llm": LLMAgent,
}


def create_agent(agent_type: str, agent_id: int, config: Dict[str, Any]):
    """
    Create an agent instance.
    
    Args:
        agent_type: Type of agent ("echo" or "llm")
        agent_id: Database ID of the agent
        config: Agent configuration dict
    
    Returns:
        Agent instance
    
    Raises:
        ValueError: If agent type is unknown
    """
    agent_class = AGENTS.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_class(agent_id, config)


__all__ = ["create_agent", "EchoAgent", "LLMAgent"]
